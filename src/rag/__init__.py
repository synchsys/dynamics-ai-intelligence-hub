"""Retrieval-augmented generation pipeline (Epic 9).

Ingestion and chunking (#67) → embeddings (#68) → Azure AI Search index (#70) →
hybrid + permission-aware retrieval (#71/#72) → cited answers (#73).
"""

from rag.ingestion import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    Chunk,
    Document,
    IngestionReport,
    IngestionResult,
    chunk_text,
    ingest,
    ingest_markdown,
    load_markdown,
    retag,
    split_markdown_sections,
)

__all__ = [
    "Document",
    "Chunk",
    "IngestionReport",
    "IngestionResult",
    "chunk_text",
    "ingest",
    "ingest_markdown",
    "load_markdown",
    "split_markdown_sections",
    "retag",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_CHUNK_OVERLAP",
]
