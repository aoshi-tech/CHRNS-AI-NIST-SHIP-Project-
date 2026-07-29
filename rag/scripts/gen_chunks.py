"""
Retrieve top-k chunks from the NCNR RAG Chroma vectorstore and print them.
No LLM call is made — use this to inspect raw retrieval results or pipe
chunk text into another tool.

Prerequisites:
  1. Ollama running locally with nomic-embed-text pulled (ollama pull nomic-embed-text)
  2. Chroma DB populated (python scripts/embed_and_ingest.py)
  3. pip install -r requirements.txt

Usage:
  python scripts/gen_chunks.py "<question>"
  python scripts/gen_chunks.py "<question>" --pack candor --top 6
  python scripts/gen_chunks.py "<question>" --max-distance 0.4 --access-level internal
"""

import argparse
import os

try:
    from _common import (
        CHROMA_PATH, COLLECTION, EMBED_MODEL, EMBED_BASE_URL,
        QUERY_PREFIX, open_vectorstore, ensure_ollama,
    )
except ImportError as exc:
    raise SystemExit(
        f"Missing dependency: {exc}\n"
        "Run: pip install -r requirements.txt"
    )
DEFAULT_TOP    = 3

# ---- query rewriting (optional, RChat-backed) ------------------------------
# Same RChat OpenAI-compatible endpoint / RCHAT_API_KEY convention as
# full_document_ingestion.py's normalization calls.
RCHAT_BASE_URL       = "https://rchat.nist.gov/api/v1"
DEFAULT_REWRITE_MODEL = "gemma-4-31B-it"

_REWRITE_SYSTEM = (
    "You rewrite user questions into clear search queries for a retrieval "
    "system over NIST NCNR neutron-scattering instrument documentation "
    "(instruments include CANDOR, VSANS, NSE, MAGIK, BT7, and shared "
    "NICE/NCNR-wide docs). Expand abbreviations, normalize instrument and "
    "workflow terminology, and make vague or terse questions explicit. "
    "Reply with ONLY the rewritten query -- no explanation, no quotes."
)


def rewrite_query(query, *, model=DEFAULT_REWRITE_MODEL, api_key=None):
    """Best-effort query rewrite via RChat. Returns (text, rewritten: bool).

    Falls back to (query, False) whenever RCHAT_API_KEY is unset or the call
    fails for any reason (network, bad response, etc.) -- rewriting is an
    accuracy enhancement, not a correctness requirement, so retrieval must
    keep working without it. Mirrors the fail-soft RChat pattern in
    scripts/agent_memory.py's _rchat_client()/search_history()."""
    key = api_key or os.environ.get("RCHAT_API_KEY", "").strip()
    if not key:
        return query, False
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key, base_url=RCHAT_BASE_URL)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _REWRITE_SYSTEM},
                {"role": "user", "content": query},
            ],
            temperature=0.0,
        )
        rewritten = (resp.choices[0].message.content or "").strip()
    except Exception:
        return query, False
    if not rewritten:
        return query, False
    return rewritten, True

ACCESS_LEVEL_MAP = {
    "public":     ["public"],
    "internal":   ["public", "internal"],
    "restricted": ["public", "internal", "restricted"],
}


def build_chroma_filter(access_level: str, pack: str | None) -> dict:
    conditions = [
        {"status": {"$eq": "current"}},
        {"access_level": {"$in": ACCESS_LEVEL_MAP[access_level]}},
    ]
    if pack:
        conditions.append({"instrument": {"$eq": pack.upper()}})
    return {"$and": conditions}


class RetrievalError(Exception):
    """Retrieval produced no usable chunks: no DB/collection, no vector match,
    or every match beyond the distance cutoff. Carries a human-readable message
    callers can surface directly (the MCP tool returns it as tool output; the
    CLI turns it into a SystemExit)."""


def retrieve(query, *, pack=None, top=DEFAULT_TOP, max_distance=0.5,
             access_level="public", vectorstore=None):
    """Return the kept (doc, score) pairs for `query`, nearest first.

    Pass an already-open Chroma handle as `vectorstore` to reuse it across calls
    (long-lived callers like mcpServer do this to avoid reconnecting every time);
    when None, a fresh one is opened -- the convenient path for the CLI and
    one-off use. Raises RetrievalError when nothing usable comes back."""
    if vectorstore is None:
        ensure_ollama()
        if not CHROMA_PATH.exists():
            raise RetrievalError(
                f"Chroma DB not found at {CHROMA_PATH}. "
                "Run: python scripts/embed_and_ingest.py"
            )
        vectorstore, _ = open_vectorstore(base_url=EMBED_BASE_URL)

    where_filter = build_chroma_filter(access_level, pack)
    docs_with_scores = vectorstore.similarity_search_with_score(
        QUERY_PREFIX + query, k=top, filter=where_filter,
    )
    if not docs_with_scores:
        raise RetrievalError(
            "No chunks matched the query and filters. "
            "Try relaxing the access level or pack filter."
        )

    kept = [(doc, score) for doc, score in docs_with_scores if score <= max_distance]
    if not kept:
        best_doc, best_distance = docs_with_scores[0]
        raise RetrievalError(
            f"No chunks within max distance {max_distance} "
            f"(closest was [{best_doc.metadata.get('source_id', 'unknown')}] "
            f"at {best_distance:.3f}). Try a larger max distance."
        )
    return kept


def format_chunks(kept):
    """Render kept (doc, score) pairs into a plain-text block -- one numbered,
    source-attributed section per chunk, nearest first."""
    blocks = []
    for i, (doc, score) in enumerate(kept, 1):
        source_id = doc.metadata.get("source_id", "unknown")
        section   = doc.metadata.get("section", "")
        url       = doc.metadata.get("source_url_or_path", "")
        header    = f"[{i}] [{source_id}]"
        if section:
            header += f" {section}"
        if url:
            header += f" — {url}"
        blocks.append(f"{header}  (distance: {score:.3f})\n" + "-" * 60 + f"\n{doc.page_content}")
    return "\n\n".join(blocks)


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve top-k chunks from the NCNR RAG vectorstore."
    )
    parser.add_argument("query", help="Natural-language question")
    parser.add_argument(
        "--pack",
        metavar="PACK",
        default=None,
        help="Filter by instrument pack: candor, vsans, nse, common (default: all)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP,
        metavar="N",
        help=f"Number of chunks to retrieve (default: {DEFAULT_TOP})",
    )
    parser.add_argument(
        "--max-distance",
        type=float,
        default=0.5,
        metavar="D",
        dest="max_distance",
        help="Drop chunks whose cosine distance exceeds this value. "
             "Cosine distance ranges 0 (identical) to 2 (opposite). "
             "Default 0.5. Pass 2 to disable.",
    )
    parser.add_argument(
        "--access-level",
        choices=list(ACCESS_LEVEL_MAP),
        default="public",
        dest="access_level",
        help="Maximum access level to include (default: public)",
    )
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help="Rewrite the query via RChat before embedding it (requires "
             "RCHAT_API_KEY). Off by default.",
    )
    parser.add_argument(
        "--rewrite-model",
        default=DEFAULT_REWRITE_MODEL,
        metavar="NAME",
        dest="rewrite_model",
        help=f"RChat model to use for --rewrite (default: {DEFAULT_REWRITE_MODEL})",
    )
    args = parser.parse_args()

    query = args.query
    try:
        if args.rewrite:
            rewritten, did_rewrite = rewrite_query(query, model=args.rewrite_model)
            if did_rewrite:
                print(f"Original:  {query}")
                print(f"Rewritten: {rewritten}\n")
                query = rewritten
            else:
                print("Rewrite skipped (no RCHAT_API_KEY or the call failed); using original query.\n")

        ensure_ollama()
        if not CHROMA_PATH.exists():
            raise RetrievalError(
                f"Chroma DB not found at {CHROMA_PATH}\n"
                "Run: python scripts/embed_and_ingest.py"
            )
        print("Connecting to Chroma ...")
        vectorstore, _embedder = open_vectorstore(base_url=EMBED_BASE_URL)
        try:
            vectorstore._collection.count()
        except Exception:
            raise RetrievalError(
                f"Collection '{COLLECTION}' not found in {CHROMA_PATH}\n"
                "Run: python scripts/embed_and_ingest.py"
            )
        print(f"Embedding query via Ollama ({EMBED_MODEL}) ...")
        print(f"Retrieving top {args.top} chunks ...")
        kept = retrieve(
            query, pack=args.pack, top=args.top,
            max_distance=args.max_distance, access_level=args.access_level,
            vectorstore=vectorstore,
        )
    except RetrievalError as exc:
        raise SystemExit(str(exc))

    print(f"Returning {len(kept)} chunks (distance <= {args.max_distance}):\n")
    print(format_chunks(kept))


if __name__ == "__main__":
    main()