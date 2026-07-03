"""Azure AI Search index — the retrieval backbone (#70).

Defines a vector + text + metadata index (including the **access tag** for
permission-aware retrieval, #72), creates it, uploads embedded chunks (#68), and
runs vector and keyword queries. Built on the ``azure-search-documents`` SDK; the
clients are injectable so the mapping/query logic is unit-testable without a live
service. Dev auth is the admin API key from the environment — no secrets in
source (Entra/Managed Identity is Epic 11).
"""

import base64
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from rag.embeddings import EmbeddedChunk
from shared.exceptions import ConfigError
from shared.logging import get_logger

_logger = get_logger("rag.index")

VECTOR_DIMENSIONS = 1536  # text-embedding-3-small
_PROFILE = "hnsw-profile"
_ALGORITHM = "hnsw"
# EDM type literals (the SDK's SearchFieldDataType constants, used as strings).
_STRING = "Edm.String"
_SINGLE_COLLECTION = "Collection(Edm.Single)"


@dataclass(frozen=True)
class SearchConfig:
    endpoint: str
    index: str
    api_key: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "SearchConfig":
        source = os.environ if env is None else env
        required = ("AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_INDEX", "AZURE_SEARCH_KEY")
        missing = [k for k in required if not source.get(k)]
        if missing:
            raise ConfigError(
                f"Missing Azure AI Search environment variables: {', '.join(missing)}"
            )
        return cls(
            endpoint=source["AZURE_SEARCH_ENDPOINT"].rstrip("/"),
            index=source["AZURE_SEARCH_INDEX"],
            api_key=source["AZURE_SEARCH_KEY"],
        )


def document_key(chunk_id: str) -> str:
    """Encode a chunk id into a valid Azure Search key (letters/digits/-/_/=)."""
    return base64.urlsafe_b64encode(chunk_id.encode("utf-8")).decode("ascii")


def build_index(name: str, *, dimensions: int = VECTOR_DIMENSIONS) -> SearchIndex:
    """The index schema: text + metadata + an HNSW vector field."""
    fields = [
        SimpleField(name="id", type=_STRING, key=True),
        SearchableField(name="content", type=_STRING),
        SimpleField(name="source", type=_STRING, filterable=True, facetable=True),
        SimpleField(name="section", type=_STRING, filterable=True),
        SimpleField(name="access_tag", type=_STRING, filterable=True),
        SearchField(
            name="vector",
            type=_SINGLE_COLLECTION,
            searchable=True,
            vector_search_dimensions=dimensions,
            vector_search_profile_name=_PROFILE,
        ),
    ]
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name=_ALGORITHM)],
        profiles=[VectorSearchProfile(name=_PROFILE, algorithm_configuration_name=_ALGORITHM)],
    )
    return SearchIndex(name=name, fields=fields, vector_search=vector_search)


def to_document(embedded: EmbeddedChunk) -> dict[str, Any]:
    """Map an embedded chunk to a search document."""
    chunk = embedded.chunk
    return {
        "id": document_key(embedded.id),
        "content": chunk.text,
        "source": chunk.source,
        "section": chunk.section or "",
        "access_tag": chunk.access_tag,
        "vector": list(embedded.vector),
    }


def _to_hit(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": result["id"],
        "content": result["content"],
        "source": result["source"],
        "section": result.get("section") or None,
        "access_tag": result["access_tag"],
        "score": result.get("@search.score"),
    }


class KnowledgeIndex:
    """Create, populate and query the knowledge index."""

    def __init__(
        self,
        config: SearchConfig,
        *,
        index_client: Any | None = None,
        search_client: Any | None = None,
        dimensions: int = VECTOR_DIMENSIONS,
    ) -> None:
        self._config = config
        self._dimensions = dimensions
        credential = AzureKeyCredential(config.api_key)
        self._index_client = index_client or SearchIndexClient(config.endpoint, credential)
        self._search_client = search_client or SearchClient(
            config.endpoint, config.index, credential
        )

    def create(self, *, recreate: bool = False) -> None:
        """Create or update the index (optionally deleting an existing one first)."""
        if recreate:
            self.delete()
        self._index_client.create_or_update_index(
            build_index(self._config.index, dimensions=self._dimensions)
        )
        _logger.info("ensured search index '%s'", self._config.index)

    def delete(self) -> None:
        self._index_client.delete_index(self._config.index)

    def upload(self, embedded: Sequence[EmbeddedChunk]) -> int:
        """Upload embedded chunks as search documents; returns the count uploaded."""
        documents = [to_document(e) for e in embedded]
        if documents:
            self._search_client.upload_documents(documents)
        _logger.info("uploaded %d document(s) to '%s'", len(documents), self._config.index)
        return len(documents)

    def keyword_search(
        self, query: str, *, top: int = 5, access_filter: str | None = None
    ) -> list[dict[str, Any]]:
        results = self._search_client.search(search_text=query, top=top, filter=access_filter)
        return [_to_hit(r) for r in results]

    def vector_search(
        self, vector: Sequence[float], *, top: int = 5, access_filter: str | None = None
    ) -> list[dict[str, Any]]:
        query = VectorizedQuery(vector=list(vector), k_nearest_neighbors=top, fields="vector")
        results = self._search_client.search(
            search_text=None, vector_queries=[query], top=top, filter=access_filter
        )
        return [_to_hit(r) for r in results]
