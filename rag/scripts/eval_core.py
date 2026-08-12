"""Shared per-question retrieval-eval core for test_retrieval_embedding.py and
evaluate_retrieval_ragas.py.

Both scripts used to independently re-implement the same fetch/filter/truncate
retrieval call and re-query Chroma+Ollama for the same questions. This module
runs retrieval once per question (`evaluate_pack_questions`) and hands back a
detail record with everything both metric families need, plus slice tags
(`expected_workflow_stage`, `expected_software`) so results can be broken down
instead of collapsed into one pack-wide average.
"""

from __future__ import annotations

import time
from pathlib import Path

from _common import QUERY_PREFIX, load_eval_questions, load_pack_chunk_ids


def percentile(values: list[float], pct: float) -> float:
    """Linear-interpolated percentile (pct in [0, 1]). 0.0 for an empty input."""
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * pct
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def context_precision_at_k(relevance: list[int]) -> float:
    """RAGAS-standard Context Precision@K from a per-rank relevance list.
    sum_k(precision@k * relevant_k) / (# relevant); 0.0 if none relevant."""
    num_relevant = sum(relevance)
    if num_relevant == 0:
        return 0.0
    total = 0.0
    hits = 0
    for k, rel in enumerate(relevance, start=1):
        hits += rel
        total += (hits / k) * rel
    return total / num_relevant


def context_recall(retrieved_source_ids: list[str], expected_sources: set[str]) -> float:
    """Fraction of expected_sources found anywhere in the retrieved list. 0.0 if
    expected_sources is empty."""
    if not expected_sources:
        return 0.0
    found = {sid for sid in retrieved_source_ids if sid in expected_sources}
    return len(found) / len(expected_sources)


def retrieve_for_question(
    query_text: str,
    *,
    pack_chunk_ids: set[str],
    vectorstore,
    embedder,
    top_n: int,
    retrieve_fn=None,
    pack_name: str | None = None,
    max_distance: float = 0.5,
    access_level: str = "public",
) -> tuple[list[dict], float]:
    """Return (retrieved_metadatas, elapsed_seconds) for one query.

    Default path over-fetches from the shared collection via a raw vector
    search and filters down to this pack's own chunk_ids -- the historical
    behavior of both eval scripts.

    When `retrieve_fn` is given (pass gen_chunks.retrieve), it's called
    instead, so the eval exercises the actual production retrieval path --
    including its max_distance cutoff and access_level/status metadata filter
    -- rather than a hand-rolled reimplementation that could silently drift
    from what mcpServer.py's gen_chunks tool really returns.
    """
    start = time.perf_counter()
    if retrieve_fn is not None:
        try:
            kept = retrieve_fn(
                query_text, pack=pack_name, top=top_n,
                max_distance=max_distance, access_level=access_level,
                vectorstore=vectorstore,
            )
        except Exception:
            kept = []
        elapsed = time.perf_counter() - start
        return [doc.metadata for doc, _score in kept], elapsed

    fetch_n = max(top_n * 2, 10)
    query_vec = embedder.embed_query(QUERY_PREFIX + query_text)
    docs = vectorstore.similarity_search_by_vector(query_vec, k=fetch_n)
    elapsed = time.perf_counter() - start
    # chunk_id is carried in metadata (set by embed_and_ingest.py) since
    # LangChain Document objects don't reliably expose the Chroma id itself.
    metas = [d.metadata for d in docs if d.metadata.get("chunk_id") in pack_chunk_ids][:top_n]
    return metas, elapsed


def evaluate_pack_questions(
    pack_name: str,
    root: Path,
    vectorstore,
    embedder,
    top_n: int,
    *,
    retrieve_fn=None,
    max_distance: float = 0.5,
    access_level: str = "public",
) -> list[dict]:
    """Run every eval question for `pack_name` through retrieval once and
    return one detail dict per question with the raw retrieval outcome plus
    slice tags. Callers derive whichever metric family they need from this
    (see topk_metrics / ragas_metrics below) instead of re-querying."""
    pack_dir = root / "context_database" / pack_name
    questions = load_eval_questions(pack_dir)
    pack_chunk_ids = load_pack_chunk_ids(pack_dir)

    details = []
    for question in questions:
        query_text = question.get("question", "")
        expected_sources = set(question.get("expected_sources", []))

        metas, elapsed = retrieve_for_question(
            query_text, pack_chunk_ids=pack_chunk_ids, vectorstore=vectorstore,
            embedder=embedder, top_n=top_n, retrieve_fn=retrieve_fn,
            pack_name=pack_name, max_distance=max_distance, access_level=access_level,
        )
        retrieved_source_ids = [m.get("source_id") for m in metas]
        relevance = [1 if sid in expected_sources else 0 for sid in retrieved_source_ids]

        hit_rank = 0
        for rank, rel in enumerate(relevance, start=1):
            if rel:
                hit_rank = rank
                break

        details.append({
            "question_id": question.get("question_id"),
            "query": query_text,
            "expected_sources": sorted(expected_sources),
            "expected_workflow_stage": question.get("expected_workflow_stage") or "unspecified",
            "expected_software": list(question.get("expected_software") or ["unspecified"]),
            "retrieved_source_ids": retrieved_source_ids,
            "relevance": relevance,
            "hit_rank": hit_rank,
            # stricter than hit_rank: every expected source (not just one) must
            # appear within top_n -- matters for multi-source questions, where
            # a single lucky hit shouldn't count as fully satisfied.
            "all_hit": bool(expected_sources) and expected_sources.issubset(set(retrieved_source_ids)),
            "elapsed_seconds": elapsed,
        })
    return details


def topk_metrics(details: list[dict]) -> dict[str, object]:
    """top-1 / top-k / all-sources accuracy, MRR, and query-time stats."""
    q = len(details)
    top1_hits = sum(1 for d in details if d["hit_rank"] == 1)
    topk_hits = sum(1 for d in details if d["hit_rank"])
    all_hits = sum(1 for d in details if d["all_hit"])
    mrr_sum = sum(1.0 / d["hit_rank"] for d in details if d["hit_rank"])
    times = [d["elapsed_seconds"] for d in details]
    return {
        "queries": q,
        "top1_accuracy": top1_hits / q if q else 0.0,
        "topk_accuracy": topk_hits / q if q else 0.0,
        "all_sources_accuracy": all_hits / q if q else 0.0,
        "mrr": mrr_sum / q if q else 0.0,
        "avg_query_time": (sum(times) / q) if q else 0.0,
        "p50_query_time": percentile(times, 0.5),
        "p95_query_time": percentile(times, 0.95),
        "total_query_time": sum(times),
    }


def ragas_metrics(details: list[dict]) -> dict[str, object]:
    """Mean Context Precision@K and Context Recall across questions."""
    q = len(details)
    precisions = [context_precision_at_k(d["relevance"]) for d in details]
    recalls = [context_recall(d["retrieved_source_ids"], set(d["expected_sources"])) for d in details]
    return {
        "queries": q,
        "mean_context_precision": (sum(precisions) / q) if q else 0.0,
        "mean_context_recall": (sum(recalls) / q) if q else 0.0,
    }


def slice_breakdown(details: list[dict], slice_key: str) -> dict[str, list[dict]]:
    """Group details by `slice_key` ('expected_workflow_stage' or
    'expected_software'). expected_software is list-valued, so a question
    tagged with multiple software packages contributes to each group."""
    groups: dict[str, list[dict]] = {}
    for d in details:
        value = d[slice_key]
        values = value if isinstance(value, list) else [value]
        for v in values:
            groups.setdefault(str(v), []).append(d)
    return groups
