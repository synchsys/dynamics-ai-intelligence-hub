"""Retrieval-augmented generation pipeline (Epic 9).

Ingestion and chunking (#67) → embeddings (#68) → Azure AI Search index (#70) →
hybrid + permission-aware retrieval (#71/#72) → cited answers (#73).
"""

from rag.embeddings import (
    DEFAULT_BATCH_SIZE,
    EmbeddedChunk,
    Embedder,
    EmbeddingCache,
    EmbeddingRun,
    InMemoryEmbeddingCache,
    content_hash,
    embed_chunks,
)
from rag.index import (
    VECTOR_DIMENSIONS,
    KnowledgeIndex,
    SearchConfig,
    build_index,
    document_key,
    to_document,
)
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
    # ingestion (#67)
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
    # embeddings (#68)
    "EmbeddedChunk",
    "EmbeddingRun",
    "Embedder",
    "EmbeddingCache",
    "InMemoryEmbeddingCache",
    "embed_chunks",
    "content_hash",
    "DEFAULT_BATCH_SIZE",
    # index (#70)
    "SearchConfig",
    "KnowledgeIndex",
    "build_index",
    "to_document",
    "document_key",
    "VECTOR_DIMENSIONS",
]
