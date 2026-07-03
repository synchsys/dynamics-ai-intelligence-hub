"""Embed document chunks for semantic retrieval (#68).

Turns ingestion chunks (#67) into vectors via the Azure OpenAI embeddings model
(``text-embedding-3-small``, 1536 dims) using the shared ``AIClient`` (#58).
Embedding is **batched** (one API call per batch) and **idempotent**: a chunk is
re-embedded only when its text changes, keyed by a content hash, so re-runs skip
unchanged chunks. Vectors feed the Azure AI Search index (#70).
"""

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import batched
from typing import Protocol, cast

from rag.ingestion import Chunk
from shared.logging import get_logger

_logger = get_logger("rag.embeddings")

DEFAULT_BATCH_SIZE = 16


class Embedder(Protocol):
    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


@dataclass(frozen=True)
class EmbeddedChunk:
    """A chunk with its embedding vector and the content hash it was embedded at."""

    chunk: Chunk
    vector: list[float]
    content_hash: str

    @property
    def id(self) -> str:
        return self.chunk.id


@dataclass(frozen=True)
class EmbeddingRun:
    """Result of an embedding pass."""

    chunks: list[EmbeddedChunk]
    embedded: int  # newly embedded this run (API calls made for these)
    reused: int  # skipped because unchanged

    @property
    def dimensions(self) -> int:
        return len(self.chunks[0].vector) if self.chunks else 0


class EmbeddingCache(Protocol):
    """Prior embeddings, so unchanged chunks can be skipped on re-runs."""

    def get(self, chunk_id: str) -> tuple[str, list[float]] | None: ...


class InMemoryEmbeddingCache:
    """A dict-backed cache, seedable from a previous run's chunks."""

    def __init__(self, embedded: Sequence[EmbeddedChunk] = ()) -> None:
        self._store: dict[str, tuple[str, list[float]]] = {
            ec.id: (ec.content_hash, ec.vector) for ec in embedded
        }

    def get(self, chunk_id: str) -> tuple[str, list[float]] | None:
        return self._store.get(chunk_id)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def embed_chunks(
    embedder: Embedder,
    chunks: Sequence[Chunk],
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    cache: EmbeddingCache | None = None,
) -> EmbeddingRun:
    """Embed ``chunks`` in batches, reusing cached vectors for unchanged chunks."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    out: list[EmbeddedChunk | None] = [None] * len(chunks)
    pending: list[tuple[int, Chunk, str]] = []
    reused = 0

    for i, chunk in enumerate(chunks):
        digest = content_hash(chunk.text)
        cached = cache.get(chunk.id) if cache is not None else None
        if cached is not None and cached[0] == digest:
            out[i] = EmbeddedChunk(chunk, list(cached[1]), digest)
            reused += 1
        else:
            pending.append((i, chunk, digest))

    embedded = 0
    for batch in batched(pending, batch_size):
        vectors = embedder.embed([chunk.text for _i, chunk, _h in batch])
        for (i, chunk, digest), vector in zip(batch, vectors, strict=True):
            out[i] = EmbeddedChunk(chunk, list(vector), digest)
            embedded += 1

    _logger.info("embedded %d chunk(s), reused %d cached", embedded, reused)
    result = cast(list[EmbeddedChunk], out)  # every slot is filled above
    return EmbeddingRun(chunks=result, embedded=embedded, reused=reused)
