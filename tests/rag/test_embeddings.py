"""Tests for RAG embeddings — batching, metadata, and idempotent re-embedding."""

from collections.abc import Sequence

import pytest

from rag import Chunk, InMemoryEmbeddingCache, content_hash, embed_chunks


class FakeEmbedder:
    """Returns a deterministic vector per text and records batch sizes."""

    def __init__(self) -> None:
        self.batches: list[int] = []
        self.total_texts = 0

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        self.batches.append(len(texts))
        self.total_texts += len(texts)
        return [[float(len(t)), 1.0, 2.0] for t in texts]


def _chunks(n: int) -> list[Chunk]:
    return [
        Chunk(source="regs.md", text=f"chunk number {i}", index=i, access_tag="public")
        for i in range(n)
    ]


def test_all_chunks_embedded_with_vectors_and_hash() -> None:
    chunks = _chunks(3)
    run = embed_chunks(FakeEmbedder(), chunks)
    assert run.embedded == 3 and run.reused == 0
    assert len(run.chunks) == 3
    assert run.dimensions == 3
    for ec, original in zip(run.chunks, chunks, strict=True):
        assert ec.chunk == original
        assert ec.content_hash == content_hash(original.text)
        assert ec.id == original.id
        assert len(ec.vector) == 3


def test_batching_respects_batch_size() -> None:
    embedder = FakeEmbedder()
    embed_chunks(embedder, _chunks(5), batch_size=2)
    assert embedder.batches == [2, 2, 1]  # 5 chunks in batches of 2
    assert embedder.total_texts == 5


def test_reembedding_is_idempotent_for_unchanged_chunks() -> None:
    chunks = _chunks(3)
    first = embed_chunks(FakeEmbedder(), chunks)
    cache = InMemoryEmbeddingCache(first.chunks)

    embedder = FakeEmbedder()
    second = embed_chunks(embedder, chunks, cache=cache)
    assert second.reused == 3 and second.embedded == 0
    assert embedder.total_texts == 0  # no API calls made
    # Vectors preserved from the cache.
    assert second.chunks[0].vector == first.chunks[0].vector


def test_changed_chunk_is_reembedded_others_reused() -> None:
    chunks = _chunks(3)
    first = embed_chunks(FakeEmbedder(), chunks)
    cache = InMemoryEmbeddingCache(first.chunks)

    # Chunk 1's text changes -> only it is re-embedded.
    changed = list(chunks)
    changed[1] = Chunk(source="regs.md", text="totally new text", index=1, access_tag="public")

    embedder = FakeEmbedder()
    run = embed_chunks(embedder, changed, cache=cache)
    assert run.embedded == 1 and run.reused == 2
    assert embedder.total_texts == 1
    # Order preserved, changed chunk carries the new hash.
    assert run.chunks[1].content_hash == content_hash("totally new text")


def test_order_is_preserved_across_cached_and_fresh() -> None:
    chunks = _chunks(4)
    first = embed_chunks(FakeEmbedder(), chunks)
    cache = InMemoryEmbeddingCache([first.chunks[0], first.chunks[2]])  # only 0 and 2 cached
    run = embed_chunks(FakeEmbedder(), chunks, cache=cache)
    assert [ec.chunk.index for ec in run.chunks] == [0, 1, 2, 3]
    assert run.reused == 2 and run.embedded == 2


def test_empty_input() -> None:
    run = embed_chunks(FakeEmbedder(), [])
    assert run.chunks == [] and run.embedded == 0 and run.dimensions == 0


def test_invalid_batch_size_raises() -> None:
    with pytest.raises(ValueError, match="batch_size must be positive"):
        embed_chunks(FakeEmbedder(), _chunks(1), batch_size=0)
