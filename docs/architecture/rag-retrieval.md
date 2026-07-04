# RAG hybrid retrieval

The query side of the RAG pipeline (#71): combine semantic (vector) and keyword
matching into ranked results that feed generation (cited answers, #73).

## Retrieval contract

```python
Retriever(index, embedder).retrieve(
    query: str, *, top_k: int = 5, access_filter: str | None = None
) -> list[RetrievedChunk]        # ordered best-first
```

`RetrievedChunk` = `id`, `content`, `source`, `section`, `access_tag`, `score`.
`as_context(chunks)` renders them into a citation-tagged block (`[id] (source ·
section)\n<content>`) for the generation prompt.

## How hybrid works

A single Azure AI Search query carries **both** a `search_text` (BM25 keyword)
leg and a `vector_queries` (HNSW vector) leg. The service runs both and fuses
their rankings with **Reciprocal Rank Fusion** — a document's score is the sum
of `1 / (k + rank)` across the two result lists — returned as `@search.score`.
The query text is embedded with the same model used at ingestion (#68) so the
vector leg is comparable to the indexed vectors.

Hybrid beats either leg alone: vector catches paraphrases the keywords miss;
keyword catches exact terms (codes, names) the embedding blurs.

## Access filtering

`access_filter` is passed straight through to the index as an OData `$filter` on
`access_tag`. It is the seam **permission-aware retrieval (#72)** fills in —
retrieval trims to what the caller may see *before* ranking, so a user never
sees a snippet of a document they can't access.

## Tuning notes

- **`top_k`** defaults to 5 — enough context for grounded answers without
  diluting the prompt. Callers lower it for tight prompts.
- On a **small corpus**, RRF scores cluster (every short doc matches common
  terms), so exact top-1 is noisy; relevance is better judged by whether the
  right chunk is in the top-k. The live check (`scripts/rag/verify_retrieval.py`)
  asserts top-2 membership on seeded queries for exactly this reason.

## Testing

`Retriever` is unit-tested with a fake index + embedder (query embedded once,
hybrid query issued with the embedded vector, `access_filter` threaded through,
hits mapped to `RetrievedChunk`, `as_context` formatting). The hybrid query
itself is tested on the index (both legs present). Live-verified end to end
against `racy-search-dev`.
