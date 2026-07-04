"""Tests for hybrid retrieval — query embedding, hybrid query, typed results."""

from collections.abc import Sequence
from typing import Any

from rag import RetrievedChunk, Retriever, as_context


class FakeEmbedder:
    def __init__(self) -> None:
        self.embedded: list[str] = []

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        self.embedded.extend(texts)
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeIndex:
    def __init__(self, hits: list[dict[str, Any]]) -> None:
        self._hits = hits
        self.calls: list[dict[str, Any]] = []

    def hybrid_search(
        self,
        query_text: str,
        vector: Sequence[float],
        *,
        top: int = 5,
        access_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        self.calls.append(
            {"query_text": query_text, "vector": list(vector), "top": top, "filter": access_filter}
        )
        return self._hits


def _hit(cid: str, section: str | None, score: float) -> dict[str, Any]:
    return {
        "id": cid,
        "content": f"content of {cid}",
        "source": "regs.md",
        "section": section,
        "access_tag": "public",
        "score": score,
    }


def test_retrieve_embeds_query_and_runs_hybrid_search() -> None:
    index = FakeIndex([_hit("a", "Overtaking", 0.9), _hit("b", "Safety", 0.7)])
    embedder = FakeEmbedder()
    chunks = Retriever(index, embedder).retrieve("when can I use DRS?", top_k=2)  # type: ignore[arg-type]

    assert embedder.embedded == ["when can I use DRS?"]  # query embedded once
    assert index.calls[0]["query_text"] == "when can I use DRS?"
    assert index.calls[0]["vector"] == [0.1, 0.2, 0.3]  # embedded vector passed through
    assert index.calls[0]["top"] == 2
    assert [c.id for c in chunks] == ["a", "b"]  # order preserved (best-first)
    assert isinstance(chunks[0], RetrievedChunk)
    assert chunks[0].section == "Overtaking" and chunks[0].score == 0.9


def test_access_filter_is_threaded_through() -> None:
    index = FakeIndex([])
    Retriever(index, FakeEmbedder()).retrieve("q", access_filter="access_tag eq 'public'")  # type: ignore[arg-type]
    assert index.calls[0]["filter"] == "access_tag eq 'public'"


def test_retrieved_chunk_from_hit_handles_missing_optional_fields() -> None:
    chunk = RetrievedChunk.from_hit(
        {"id": "x", "content": "c", "source": "s", "access_tag": "public"}
    )
    assert chunk.section is None and chunk.score is None


def test_as_context_formats_citations() -> None:
    chunks = [
        RetrievedChunk("regs.md#0", "DRS rules", "regs.md", "Overtaking", "public", 0.9),
        RetrievedChunk("regs.md#1", "hold position", "regs.md", None, "public", 0.7),
    ]
    context = as_context(chunks)
    assert "[regs.md#0] (regs.md · Overtaking)" in context
    assert "DRS rules" in context
    assert "[regs.md#1] (regs.md)" in context  # no section -> no separator


def test_as_context_empty() -> None:
    assert as_context([]) == "(no relevant sources found)"
