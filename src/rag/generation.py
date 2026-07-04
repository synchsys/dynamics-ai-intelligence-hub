"""Grounded generation with citations — the answer side of RAG (#73).

Takes retrieved chunks (#71), grounds the model in them, and returns a
:class:`CitedAnswer`: the answer plus **structured citations** that are resolved
back to the retrieved chunks. Citations the model invents (ids not in the
retrieved set) are dropped, so every returned citation provably maps to a source
the caller was allowed to retrieve (#72). Uses prompting + structured output
(#60) on the shared ``AIClient`` (#58).
"""

from collections.abc import Sequence
from dataclasses import dataclass

from pydantic import BaseModel, Field

from ai.client import AIClient
from ai.structured import structured_output
from rag.retrieval import RetrievedChunk, as_context
from shared.logging import get_logger

_logger = get_logger("rag.generation")

_SYSTEM = (
    "You answer questions using ONLY the numbered sources provided. Each source "
    "is prefixed with its id in square brackets, e.g. [regs.md#0]. Cite the id of "
    "every source you rely on in the 'citations' list. If the sources do not "
    "contain the answer, say so plainly and return an empty citations list — never "
    "invent facts or sources.\n\nSources:\n{context}"
)

_NO_SOURCES = "I don't have any sources to answer that question."


class _RawAnswer(BaseModel):
    """The model's structured reply before citation resolution."""

    answer: str = Field(description="The answer, grounded only in the provided sources")
    citations: list[str] = Field(
        default_factory=list, description="Ids of the sources actually used, e.g. ['regs.md#0']"
    )


@dataclass(frozen=True)
class Citation:
    """A resolved citation pointing at a retrieved chunk."""

    id: str
    source: str
    section: str | None


@dataclass(frozen=True)
class CitedAnswer:
    """A grounded answer plus the sources it cites."""

    answer: str
    citations: list[Citation]

    @property
    def is_grounded(self) -> bool:
        return bool(self.citations)


def generate_answer(
    client: AIClient,
    question: str,
    chunks: Sequence[RetrievedChunk],
    *,
    max_repair: int = 1,
) -> CitedAnswer:
    """Answer ``question`` grounded in ``chunks``, returning resolved citations.

    Citations are resolved against the retrieved chunk ids — any id the model
    returns that was not retrieved is discarded (deduped, order-preserved), so a
    returned citation always maps to a real, permitted source.
    """
    if not chunks:
        return CitedAnswer(answer=_NO_SOURCES, citations=[])

    messages = [
        {"role": "system", "content": _SYSTEM.format(context=as_context(chunks))},
        {"role": "user", "content": question},
    ]
    raw = structured_output(client, messages, _RawAnswer, max_repair=max_repair)

    by_id = {chunk.id: chunk for chunk in chunks}
    citations: list[Citation] = []
    seen: set[str] = set()
    for cited_id in raw.citations:
        chunk = by_id.get(cited_id)
        if chunk is not None and cited_id not in seen:
            seen.add(cited_id)
            citations.append(Citation(id=chunk.id, source=chunk.source, section=chunk.section))

    dropped = len(raw.citations) - len(citations)
    if dropped:
        _logger.warning("dropped %d citation(s) not matching a retrieved chunk", dropped)
    return CitedAnswer(answer=raw.answer, citations=citations)
