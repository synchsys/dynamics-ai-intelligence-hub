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

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from rag.embeddings import Embedder
from rag.index import KnowledgeIndex
from shared.logging import get_logger

_logger = get_logger("rag.retrieval")

DEFAULT_TOP_K = 5

# Access-tag hierarchy: each level implicitly grants the ones before it.
ACCESS_LEVELS: tuple[str, ...] = ("public", "internal", "confidential")

# Dataverse security role -> the highest access tag it grants. Policy is owned by
# Epic 11 (11.B); this is the default mapping the retrieval layer enforces.
DEFAULT_ROLE_ACCESS: dict[str, str] = {
    "guest": "public",
    "reader": "public",
    "employee": "internal",
    "salesperson": "internal",
    "manager": "confidential",
    "administrator": "confidential",
}

# A filter that matches no document — deny-by-default for unknown/unprivileged roles.
_DENY_ALL = "access_tag eq '__no_access__'"


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


@dataclass(frozen=True)
class AccessPolicy:
    """Maps a caller's roles to allowed access tags and a search filter.

    Deny-by-default: unknown/unprivileged roles resolve to no tags and a filter
    that matches nothing, so retrieval never leaks a document the caller's role
    does not grant.
    """

    role_access: Mapping[str, str] = field(default_factory=lambda: dict(DEFAULT_ROLE_ACCESS))

    def allowed_tags(self, roles: Iterable[str]) -> set[str]:
        highest = -1
        for role in roles:
            tag = self.role_access.get(role.strip().casefold())
            if tag is not None:
                highest = max(highest, ACCESS_LEVELS.index(tag))
        return set(ACCESS_LEVELS[: highest + 1]) if highest >= 0 else set()

    def filter_for(self, roles: Iterable[str]) -> str:
        """Build the OData security filter for ``roles`` (deny-all if none granted)."""
        tags = self.allowed_tags(roles)
        if not tags:
            return _DENY_ALL
        joined = ",".join(sorted(tags))
        return f"search.in(access_tag, '{joined}', ',')"


DEFAULT_POLICY = AccessPolicy()


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

    def retrieve_for(
        self,
        query: str,
        roles: Iterable[str],
        *,
        top_k: int = DEFAULT_TOP_K,
        policy: AccessPolicy = DEFAULT_POLICY,
    ) -> list[RetrievedChunk]:
        """Permission-aware retrieval: trim results to what ``roles`` may access."""
        return self.retrieve(query, top_k=top_k, access_filter=policy.filter_for(roles))


def as_context(chunks: Sequence[RetrievedChunk]) -> str:
    """Format retrieved chunks as a citation-tagged context block for generation."""
    if not chunks:
        return "(no relevant sources found)"
    blocks = []
    for chunk in chunks:
        label = f"{chunk.source}" + (f" · {chunk.section}" if chunk.section else "")
        blocks.append(f"[{chunk.id}] ({label})\n{chunk.content}")
    return "\n\n".join(blocks)
