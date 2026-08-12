"""Headless evaluation harness for scripts/app.py's chat agent.

Drives the exact same LangGraph agent app.py builds for a real request --
same system prompt (SYSTEM_INSTRUCTION), same MCP + NCNR-metadata tool set,
same per-message tool scoping (_scoped_tools), same sampling params -- against
a fixed question set (scripts/eval/agent_eval_questions.jsonl), without
starting the FastAPI server. For each question it grades:

  - answer correctness: deterministic keyword match against the question's
    answer_should_include / answer_should_not_include fields.
  - tool-call correctness: whether every tool in expected_tools was actually
    called (extra/unexpected tool calls are recorded but don't fail a run).
  - latency/token usage: via app.py's _TurnMetrics, the same per-model-call
    and per-tool timing /chat/stream reports over SSE, here written to disk
    instead of only logged to stdout.

Needs network access (the real RChat/reductus/NCNR/NCNR-metadata-OpenAPI
servers -- no mocking, same philosophy as the old scripts/test_reductus_tools.py)
and RCHAT_API_KEY (or another provider's key) in .env.

Usage:
  python scripts/eval_agent.py [--questions PATH] [--category CAT]
                                [--model NAME] [--output-csv FILE]
                                [--output-html FILE] [--detail]
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import importlib.util
import json
import os
import statistics
import sys
import unicodedata
from pathlib import Path

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# Windows consoles default stdout to the system codepage (cp1252), which can't
# encode characters that show up routinely in agent answers (en/em dashes,
# degree/tolerance symbols, non-breaking hyphens) and crashes print() mid-run.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_PY = REPO_ROOT / "scripts" / "app.py"
DEFAULT_QUESTIONS = REPO_ROOT / "scripts" / "eval" / "agent_eval_questions.jsonl"
DEFAULT_RESULTS_DIR = REPO_ROOT / "scripts" / "eval" / "results"
# Only rchat model that handles multi-tool auto tool-choice correctly (see
# the same note in agent.py / app.py's MODEL_CATALOG comment).
DEFAULT_MODEL = "gpt-oss-120b"

# The model consistently writes "smart" typography (non-breaking/narrow
# hyphens and spaces, e.g. U+202F between a number and its unit; curly
# quotes) even when a question's answer_should_include uses plain ASCII
# punctuation, which would otherwise fail a literally-correct answer on a
# substring technicality unrelated to content correctness. Unicode defines
# many space-separator code points (regular, non-breaking, narrow no-break,
# em/en/thin, ...) -- normalizing by Unicode category catches all of them
# instead of hand-listing individual code points one crash report at a time.
_PUNCTUATION_NORMALIZE = str.maketrans({
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",
    "‘": "'", "’": "'", "“": '"', "”": '"',
})


def _normalize(text: str) -> str:
    text = text.translate(_PUNCTUATION_NORMALIZE)
    return "".join(" " if unicodedata.category(ch) == "Zs" else ch for ch in text)


DETAIL_CSV_FIELDS = [
    "question_id", "category", "answer_correct", "tools_correct",
    "wall_s", "model_calls", "sum_model_s", "tool_calls", "sum_tool_s",
    "in_tokens", "out_tokens",
    "expected_tools", "actual_tools", "missing_tools", "extra_tools",
    "missing_include", "forbidden_hit", "error", "answer",
]
SUMMARY_CSV_FIELDS = [
    "category", "n_questions", "answer_accuracy", "tool_accuracy",
    "avg_wall_s", "avg_model_calls", "avg_tool_calls",
    "avg_in_tokens", "avg_out_tokens",
]

# Load app.py the same way app.py/agent.py load mcpServer.py, so this reuses
# app.py's live SYSTEM_INSTRUCTION, mcp_server_tools, sampling params, and
# _TurnMetrics instead of a hand-rolled copy that can silently drift from
# production. Importing it (unlike running it) never starts uvicorn or the
# FastAPI lifespan -- those only run under `if __name__ == "__main__"` /
# ASGI startup respectively.
_spec = importlib.util.spec_from_file_location("app", APP_PY)
app_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["app"] = app_mod
_spec.loader.exec_module(app_mod)  # type: ignore[union-attr]


def load_questions(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_csv(rows: list[dict], fieldnames: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_llm(model: str):
    """Mirror app.py's _build_agent LLM branch, minus the FastAPI/api_keys
    plumbing -- this is a batch offline run, so the key always comes from
    the environment (app_mod.SERVER_API_KEYS), same as agent.py's rchat_key."""
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI

    provider = app_mod._provider_for_model(model)
    api_key = app_mod.SERVER_API_KEYS.get(provider, "")
    if not api_key:
        raise RuntimeError(
            f"Missing {provider} API key for model '{model}' -- set it in .env."
        )

    openai_kwargs = {"max_tokens": app_mod.MAX_OUTPUT_TOKENS}
    if model != "gemma-4-31B-it":
        openai_kwargs["model_kwargs"] = {"frequency_penalty": app_mod.FREQUENCY_PENALTY}

    if provider == "openai":
        return app_mod.ReasoningChatOpenAI(
            model=model, api_key=api_key, temperature=app_mod.SAMPLING_TEMPERATURE, **openai_kwargs
        )
    if provider == "anthropic":
        return ChatAnthropic(
            model=model, anthropic_api_key=api_key,
            temperature=app_mod.SAMPLING_TEMPERATURE, max_tokens=app_mod.MAX_OUTPUT_TOKENS,
        )
    if provider == "google":
        return ChatGoogleGenerativeAI(
            model=model, google_api_key=api_key,
            temperature=app_mod.SAMPLING_TEMPERATURE, max_output_tokens=app_mod.MAX_OUTPUT_TOKENS,
        )
    if provider == "rchat":
        return app_mod.ReasoningChatOpenAI(
            model=model, api_key=api_key, base_url=app_mod.RCHAT_BASE_URL,
            temperature=app_mod.SAMPLING_TEMPERATURE, **openai_kwargs,
        )
    raise RuntimeError(f"Unsupported provider '{provider}' for model '{model}'.")


async def load_all_tools() -> list:
    """Rebuild the same tool set app.py's lifespan() assembles: the local
    MCP-wrapped tools (app_mod.mcp_server_tools) plus the external NCNR
    metadata OpenAPI tools, without needing a running FastAPI app."""
    from langchain_mcp_adapters.client import MultiServerMCPClient

    npx_cmd = app_mod._resolve_npx()
    mcp_env = dict(os.environ)
    npx_dir = str(Path(npx_cmd).parent)
    if os.path.isdir(npx_dir):
        mcp_env["PATH"] = npx_dir + os.pathsep + mcp_env.get("PATH", "")
    mcp_client = MultiServerMCPClient({
        "ncnr-api-server": {
            "transport": "stdio",
            "command": npx_cmd,
            "args": [
                "--yes",
                "@ivotoby/openapi-mcp-server",
                "--api-base-url", "https://ncnr.nist.gov/ncnrdata/metadata/api/v1",
                "--openapi-spec", str(REPO_ROOT / "openAPI.json"),
            ],
            "env": mcp_env,
        },
    })
    return await mcp_client.get_tools() + app_mod.mcp_server_tools


async def run_question(llm, all_tools: list, record: dict, model: str) -> dict:
    question = record["question"]
    tools = app_mod._scoped_tools(all_tools, question)
    agent_executor = app_mod.create_agent(
        model=llm,
        tools=tools,
        system_prompt=app_mod.SYSTEM_INSTRUCTION,
        checkpointer=MemorySaver(),
    )
    config = {
        "configurable": {"thread_id": f"eval-{record['question_id']}"},
        "recursion_limit": app_mod.AGENT_RECURSION_LIMIT,
    }
    metrics = app_mod._TurnMetrics(model, record["question_id"])
    answer_parts: list[str] = []
    actual_tools: list[str] = []
    error = None

    try:
        async for event in agent_executor.astream_events(
            {"messages": [("user", question)]}, config=config, version="v2",
        ):
            kind = event["event"]
            name = event.get("name", "")
            run_id = event.get("run_id")

            if kind == "on_chat_model_start":
                metrics.model_start(run_id)
            elif kind == "on_chat_model_end":
                out = event["data"].get("output")
                metrics.model_end(run_id, getattr(out, "usage_metadata", None))
            elif kind == "on_tool_start":
                metrics.tool_start(run_id, name)
                actual_tools.append(name)
            elif kind == "on_tool_end":
                metrics.tool_end(run_id, name)
            elif kind == "on_chat_model_stream":
                metrics.model_first_token(run_id)
                chunk = event["data"].get("chunk")
                if chunk and not getattr(chunk, "tool_call_chunks", None):
                    content = getattr(chunk, "content", "")
                    if isinstance(content, str) and content:
                        answer_parts.append(content)
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                t = block.get("text", "")
                                if t:
                                    answer_parts.append(t)
    except Exception as exc:  # noqa: BLE001 - record as a failed run, keep evaluating the rest
        error = f"{type(exc).__name__}: {exc}"

    answer = "".join(answer_parts)
    answer_normalized = _normalize(answer).lower()
    include = record.get("answer_should_include") or []
    exclude = record.get("answer_should_not_include") or []
    missing_include = [s for s in include if _normalize(s).lower() not in answer_normalized]
    forbidden_hit = [s for s in exclude if _normalize(s).lower() in answer_normalized]
    answer_correct = error is None and not missing_include and not forbidden_hit

    expected_tools = set(record.get("expected_tools") or [])
    actual_tools_set = set(actual_tools)
    missing_tools = sorted(expected_tools - actual_tools_set)
    extra_tools = sorted(actual_tools_set - expected_tools)
    tools_correct = error is None and not missing_tools

    summary = metrics.summary()
    return {
        "question_id": record["question_id"],
        "category": record.get("category", ""),
        "question": question,
        "answer": answer,
        "error": error or "",
        "answer_correct": answer_correct,
        "missing_include": "; ".join(missing_include),
        "forbidden_hit": "; ".join(forbidden_hit),
        "tools_correct": tools_correct,
        "expected_tools": "; ".join(sorted(expected_tools)),
        "actual_tools": "; ".join(actual_tools),
        "missing_tools": "; ".join(missing_tools),
        "extra_tools": "; ".join(extra_tools),
        "wall_s": summary["wall_s"],
        "model_calls": summary["model_calls"],
        "sum_model_s": summary["sum_model_s"],
        "tool_calls": summary["tool_calls"],
        "sum_tool_s": summary["sum_tool_s"],
        "in_tokens": sum(c["in_tokens"] or 0 for c in summary["model_call_detail"]),
        "out_tokens": sum(c["out_tokens"] or 0 for c in summary["model_call_detail"]),
    }


def aggregate(results: list[dict]) -> list[dict]:
    by_category: dict[str, list[dict]] = {}
    for r in results:
        by_category.setdefault(r["category"], []).append(r)

    rows = []
    for category in [*sorted(by_category), "ALL"]:
        items = results if category == "ALL" else by_category[category]
        n = len(items)
        rows.append({
            "category": category,
            "n_questions": n,
            "answer_accuracy": round(sum(r["answer_correct"] for r in items) / n, 3),
            "tool_accuracy": round(sum(r["tools_correct"] for r in items) / n, 3),
            "avg_wall_s": round(statistics.mean(r["wall_s"] for r in items), 3),
            "avg_model_calls": round(statistics.mean(r["model_calls"] for r in items), 2),
            "avg_tool_calls": round(statistics.mean(r["tool_calls"] for r in items), 2),
            "avg_in_tokens": round(statistics.mean(r["in_tokens"] for r in items), 1),
            "avg_out_tokens": round(statistics.mean(r["out_tokens"] for r in items), 1),
        })
    return rows


def write_html_report(category_rows: list[dict], path: Path) -> None:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    categories = [r["category"] for r in category_rows]
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "table", "colspan": 2}, None],
               [{"type": "xy"}, {"type": "xy"}]],
        subplot_titles=("Per-category summary", "Accuracy by category", "Avg wall time (s) by category"),
        row_heights=[0.45, 0.55],
        vertical_spacing=0.12,
    )
    header = list(category_rows[0].keys())
    fig.add_trace(
        go.Table(
            header=dict(values=[h.replace("_", " ") for h in header], align="left"),
            cells=dict(values=[[r[h] for r in category_rows] for h in header], align="left"),
        ),
        row=1, col=1,
    )
    fig.add_trace(go.Bar(name="Answer accuracy", x=categories, y=[r["answer_accuracy"] for r in category_rows]), row=2, col=1)
    fig.add_trace(go.Bar(name="Tool accuracy", x=categories, y=[r["tool_accuracy"] for r in category_rows]), row=2, col=1)
    fig.add_trace(go.Bar(name="Avg wall (s)", x=categories, y=[r["avg_wall_s"] for r in category_rows], showlegend=False), row=2, col=2)
    fig.update_layout(barmode="group", title="scripts/app.py agent evaluation report", height=800)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(path), include_plotlyjs=True)


def _print_detail(result: dict) -> None:
    print("-" * 80)
    print(f"question_id: {result['question_id']} ({result['category']})")
    print(f"question: {result['question']}")
    print(f"answer: {result['answer'][:500]}")
    if result["error"]:
        print(f"error: {result['error']}")
    if result["missing_include"]:
        print(f"missing_include: {result['missing_include']}")
    if result["forbidden_hit"]:
        print(f"forbidden_hit: {result['forbidden_hit']}")
    if result["missing_tools"]:
        print(f"missing_tools: {result['missing_tools']} (called: {result['actual_tools']})")
    if result["extra_tools"]:
        print(f"extra_tools: {result['extra_tools']}")
    print(f"wall_s={result['wall_s']} model_calls={result['model_calls']} tool_calls={result['tool_calls']}")


async def _main_async(args: argparse.Namespace) -> int:
    questions = load_questions(args.questions)
    if args.category:
        questions = [q for q in questions if q.get("category") == args.category]
    if not questions:
        print(f"No questions found (questions={args.questions}, category={args.category!r}).", file=sys.stderr)
        return 2

    llm = build_llm(args.model)
    all_tools = await load_all_tools()

    results = []
    for record in questions:
        print(f"Running {record['question_id']} ({record.get('category', '')})...")
        result = await run_question(llm, all_tools, record, args.model)
        results.append(result)
        status = "PASS" if result["answer_correct"] and result["tools_correct"] else "FAIL"
        print(
            f"  [{status}] answer_correct={result['answer_correct']} "
            f"tools_correct={result['tools_correct']} wall={result['wall_s']}s"
        )
        if args.detail:
            _print_detail(result)

    category_rows = aggregate(results)
    print("\n" + "=" * 80)
    print(f"{'category':<15} {'n':>4} {'answer_acc':>11} {'tool_acc':>9} {'avg_wall_s':>11}")
    for row in category_rows:
        print(
            f"{row['category']:<15} {row['n_questions']:>4} "
            f"{row['answer_accuracy']:>11} {row['tool_accuracy']:>9} {row['avg_wall_s']:>11}"
        )

    write_csv(results, DETAIL_CSV_FIELDS, args.output_csv)
    print(f"\nWrote {args.output_csv}")
    write_html_report(category_rows, args.output_html)
    print(f"Wrote {args.output_html}")

    return 0 if all(r["answer_correct"] and r["tools_correct"] for r in results) else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate scripts/app.py's chat agent end-to-end.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--category", default=None, help="Only run questions in this category.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_RESULTS_DIR / "agent_eval_results.csv")
    parser.add_argument("--output-html", type=Path, default=DEFAULT_RESULTS_DIR / "agent_eval_report.html")
    parser.add_argument("--detail", action="store_true")
    args = parser.parse_args()
    sys.exit(asyncio.run(_main_async(args)))


if __name__ == "__main__":
    main()
