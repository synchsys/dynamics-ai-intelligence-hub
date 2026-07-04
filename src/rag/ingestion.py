"""Document ingestion and chunking for the RAG pipeline (#67).

Loads knowledge sources (markdown/text), splits them into overlapping chunks,
and attaches retrieval metadata — crucially the **access tag** that
permission-aware retrieval (#72) filters on. Chunks are the units later embedded
(#68) and indexed in Azure AI Search (#70). Pure and dependency-free so chunking
choices are unit-testable; the size/overlap choice is recorded in
``docs/architecture/rag-ingestion.md``.
"""

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace

# Recorded chunking defaults (characters). See docs/architecture/rag-ingestion.md.
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


@dataclass(frozen=True)
class Document:
    """A knowledge source (or one section of one) ready to chunk."""

    source: str
    text: str
    access_tag: str = "public"
    section: str | None = None


@dataclass(frozen=True)
class Chunk:
    """An embed-ready unit with its provenance and access metadata."""

    source: str
    text: str
    index: int
    access_tag: str
    section: str | None = None

    @property
    def id(self) -> str:
        return f"{self.source}#{self.index}"


@dataclass(frozen=True)
class IngestionReport:
    """Summary of an ingestion run."""

    documents: int
    chunks: int
    average_chunk_size: float


@dataclass(frozen=True)
class IngestionResult:
    chunks: list[Chunk]
    report: IngestionReport


def chunk_text(
    text: str, *, size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP
) -> list[str]:
    """Split ``text`` into overlapping, word-boundary-snapped chunks of ~``size`` chars."""
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= overlap < size:
        raise ValueError("overlap must be in [0, size)")

    norm = " ".join(text.split())
    if not norm:
        return []

    chunks: list[str] = []
    start, n = 0, len(norm)
    while True:  # start < n holds on entry and after each step; termination is via break
        end = min(start + size, n)
        if end < n:  # snap the cut back to a word boundary within the window
            boundary = norm.rfind(" ", start + 1, end)
            if boundary != -1:
                end = boundary
        chunks.append(norm[start:end].strip())
        if end >= n:
            break
        # start the next chunk `overlap` chars earlier, snapped to a word boundary
        target = end - overlap
        boundary = norm.rfind(" ", start + 1, target)
        start = boundary + 1 if boundary != -1 else end
    return [c for c in chunks if c]


def split_markdown_sections(text: str) -> list[tuple[str | None, str]]:
    """Split markdown into ``(section_title, body)`` pairs by heading.

    Content before the first heading is returned with a ``None`` title.
    """
    matches = list(_HEADING.finditer(text))
    if not matches:
        return [(None, text)] if text.strip() else []

    sections: list[tuple[str | None, str]] = []
    preamble = text[: matches[0].start()].strip()
    if preamble:
        sections.append((None, preamble))
    for i, match in enumerate(matches):
        title = match.group(2).strip()
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        if body:
            sections.append((title, body))
    return sections


def load_markdown(source: str, text: str, *, access_tag: str = "public") -> list[Document]:
    """Load a markdown source into one :class:`Document` per section."""
    return [
        Document(source=source, text=body, access_tag=access_tag, section=title)
        for title, body in split_markdown_sections(text)
    ]


def ingest(
    documents: Iterable[Document],
    *,
    size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> IngestionResult:
    """Chunk each document, carrying source/section/access-tag metadata onto every chunk."""
    chunks: list[Chunk] = []
    doc_count = 0
    # A per-source running index so chunks from different sections of the same
    # source get distinct ids (source#index) — the id is the search-doc key (#70).
    next_index: dict[str, int] = {}
    for doc in documents:
        doc_count += 1
        for piece in chunk_text(doc.text, size=size, overlap=overlap):
            index = next_index.get(doc.source, 0)
            next_index[doc.source] = index + 1
            chunks.append(
                Chunk(
                    source=doc.source,
                    text=piece,
                    index=index,
                    access_tag=doc.access_tag,
                    section=doc.section,
                )
            )
    total = sum(len(c.text) for c in chunks)
    average = total / len(chunks) if chunks else 0.0
    return IngestionResult(
        chunks=chunks,
        report=IngestionReport(
            documents=doc_count, chunks=len(chunks), average_chunk_size=round(average, 1)
        ),
    )


def ingest_markdown(
    sources: Sequence[tuple[str, str, str]],
    *,
    size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> IngestionResult:
    """Convenience: ingest ``(source, text, access_tag)`` markdown sources end to end."""
    documents: list[Document] = []
    for source, text, access_tag in sources:
        documents.extend(load_markdown(source, text, access_tag=access_tag))
    return ingest(documents, size=size, overlap=overlap)


def retag(document: Document, access_tag: str) -> Document:
    """Return a copy of ``document`` with a different access tag."""
    return replace(document, access_tag=access_tag)
