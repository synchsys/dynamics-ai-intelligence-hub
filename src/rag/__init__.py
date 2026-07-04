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
from rag.generation import Citation, CitedAnswer, generate_answer
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
from rag.retrieval import (
    ACCESS_LEVELS,
    DEFAULT_POLICY,
    DEFAULT_ROLE_ACCESS,
    DEFAULT_TOP_K,
    AccessPolicy,
    RetrievedChunk,
    Retriever,
    as_context,
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
    # retrieval (#71)
    "Retriever",
    "RetrievedChunk",
    "as_context",
    "DEFAULT_TOP_K",
    # permission-aware retrieval (#72)
    "AccessPolicy",
    "DEFAULT_POLICY",
    "ACCESS_LEVELS",
    "DEFAULT_ROLE_ACCESS",
    # generation (#73)
    "generate_answer",
    "CitedAnswer",
    "Citation",
]
