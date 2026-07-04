"""Hybrid retrieval — the query side of the RAG pipeline (#71).

Combines semantic (vector) and keyword matching in a single Azure AI Search
hybrid query (fused by Reciprocal Rank Fusion) and returns ranked, typed
:class:`RetrievedChunk`s with provenance. The query text is embedded with the
same model used at ingestion (#68). ``access_filter`` is threaded straight
through to the index — the seam permission-aware retrieval (#72) fills in.

Retrieval contract: ``retrieve(query, *, top_k, access_filter) ->
list[RetrievedChunk]``, ordered best-first. This is what feeds generation
(cited answers, #73).
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from rag.embeddings import Embedder
from rag.index import KnowledgeIndex
from shared.logging import get_logger

_logger = get_logger("rag.retrieval")

DEFAULT_TOP_K = 5


@dataclass(frozen=True)
class RetrievedChunk:
    """A retrieved chunk with its fused relevance score and provenance."""

    id: str
    content: str
    source: str
    section: str | None
    access_tag: str
    score: float | None

    @classmethod
    def from_hit(cls, hit: dict[str, Any]) -> "RetrievedChunk":
        return cls(
            id=hit["id"],
            content=hit["content"],
            source=hit["source"],
            section=hit.get("section"),
            access_tag=hit["access_tag"],
            score=hit.get("score"),
        )


@dataclass
class Retriever:
    """Hybrid retrieval over the knowledge index."""

    index: KnowledgeIndex
    embedder: Embedder

    def retrieve(
        self, query: str, *, top_k: int = DEFAULT_TOP_K, access_filter: str | None = None
    ) -> list[RetrievedChunk]:
        """Return the top-``top_k`` chunks for ``query`` via a hybrid query, best-first."""
        vector = self.embedder.embed([query])[0]
        hits = self.index.hybrid_search(query, vector, top=top_k, access_filter=access_filter)
        _logger.info("hybrid retrieval for %r returned %d hit(s)", query[:60], len(hits))
        return [RetrievedChunk.from_hit(hit) for hit in hits]


def as_context(chunks: Sequence[RetrievedChunk]) -> str:
    """Format retrieved chunks as a citation-tagged context block for generation."""
    if not chunks:
        return "(no relevant sources found)"
    blocks = []
    for chunk in chunks:
        label = f"{chunk.source}" + (f" · {chunk.section}" if chunk.section else "")
        blocks.append(f"[{chunk.id}] ({label})\n{chunk.content}")
    return "\n\n".join(blocks)
