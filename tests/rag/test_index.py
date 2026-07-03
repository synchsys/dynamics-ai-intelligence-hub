"""Tests for the Azure AI Search index — schema, mapping, and client wiring."""

import base64
from typing import Any

import pytest

import rag.index as index_mod
from rag import Chunk
from rag.embeddings import EmbeddedChunk
from rag.index import (
    KnowledgeIndex,
    SearchConfig,
    build_index,
    document_key,
    to_document,
)
from shared.exceptions import ConfigError

CONFIG = SearchConfig(endpoint="https://x.search.windows.net", index="racy-knowledge", api_key="k")


def _embedded(chunk_id_source: str = "regs.md", index: int = 0) -> EmbeddedChunk:
    chunk = Chunk(
        source=chunk_id_source,
        text="body text",
        index=index,
        access_tag="internal",
        section="Rules",
    )
    return EmbeddedChunk(chunk=chunk, vector=[0.1, 0.2, 0.3], content_hash="h")


# --- config -----------------------------------------------------------------


def test_config_from_env() -> None:
    cfg = SearchConfig.from_env(
        {
            "AZURE_SEARCH_ENDPOINT": "https://x.search.windows.net/",
            "AZURE_SEARCH_INDEX": "idx",
            "AZURE_SEARCH_KEY": "secret",
        }
    )
    assert cfg.endpoint == "https://x.search.windows.net"  # trailing slash stripped
    assert cfg.index == "idx"


def test_config_missing_raises() -> None:
    with pytest.raises(ConfigError, match="AZURE_SEARCH_KEY"):
        SearchConfig.from_env({"AZURE_SEARCH_ENDPOINT": "https://x", "AZURE_SEARCH_INDEX": "i"})


# --- schema + mapping -------------------------------------------------------


def test_document_key_is_reversible_and_valid() -> None:
    key = document_key("regs.md#3")
    assert base64.urlsafe_b64decode(key).decode() == "regs.md#3"
    assert all(c.isalnum() or c in "-_=" for c in key)  # valid Azure Search key chars


def test_build_index_schema() -> None:
    idx = build_index("racy-knowledge", dimensions=1536)
    assert idx.name == "racy-knowledge"
    by_name = {f.name: f for f in idx.fields}
    assert set(by_name) == {"id", "content", "source", "section", "access_tag", "vector"}
    assert by_name["id"].key is True
    assert by_name["vector"].vector_search_dimensions == 1536
    assert by_name["vector"].vector_search_profile_name == "hnsw-profile"
    assert idx.vector_search is not None
    assert idx.vector_search.profiles and idx.vector_search.profiles[0].name == "hnsw-profile"
    assert idx.vector_search.algorithms and idx.vector_search.algorithms[0].name == "hnsw"


def test_to_document_maps_fields_and_encodes_key() -> None:
    doc = to_document(_embedded())
    assert doc["id"] == document_key("regs.md#0")
    assert doc["content"] == "body text"
    assert doc["source"] == "regs.md"
    assert doc["section"] == "Rules"
    assert doc["access_tag"] == "internal"
    assert doc["vector"] == [0.1, 0.2, 0.3]


def test_to_document_blank_section_when_none() -> None:
    ec = EmbeddedChunk(Chunk("s", "t", 0, "public", section=None), [0.0], "h")
    assert to_document(ec)["section"] == ""


# --- client wiring ----------------------------------------------------------


class FakeIndexClient:
    def __init__(self) -> None:
        self.created: list[Any] = []
        self.deleted: list[str] = []

    def create_or_update_index(self, index: Any) -> None:
        self.created.append(index)

    def delete_index(self, name: str) -> None:
        self.deleted.append(name)


class FakeSearchClient:
    def __init__(self, results: list[dict[str, Any]] | None = None) -> None:
        self.uploaded: list[list[dict[str, Any]]] = []
        self.searches: list[dict[str, Any]] = []
        self._results = results or []

    def upload_documents(self, documents: list[dict[str, Any]]) -> None:
        self.uploaded.append(documents)

    def search(self, **kwargs: Any) -> Any:
        self.searches.append(kwargs)
        return iter(self._results)


def _index(
    results: list[dict[str, Any]] | None = None,
) -> tuple[KnowledgeIndex, FakeIndexClient, FakeSearchClient]:
    ic, sc = FakeIndexClient(), FakeSearchClient(results)
    return KnowledgeIndex(CONFIG, index_client=ic, search_client=sc), ic, sc


def test_create_builds_and_submits_index() -> None:
    ki, ic, _ = _index()
    ki.create()
    assert ic.created[0].name == "racy-knowledge"
    assert ic.deleted == []


def test_recreate_deletes_first() -> None:
    ki, ic, _ = _index()
    ki.create(recreate=True)
    assert ic.deleted == ["racy-knowledge"]
    assert len(ic.created) == 1


def test_delete_calls_client() -> None:
    ki, ic, _ = _index()
    ki.delete()
    assert ic.deleted == ["racy-knowledge"]


def test_upload_maps_and_counts() -> None:
    ki, _, sc = _index()
    n = ki.upload([_embedded(index=0), _embedded(index=1)])
    assert n == 2
    assert len(sc.uploaded[0]) == 2
    assert sc.uploaded[0][0]["source"] == "regs.md"


def test_upload_empty_makes_no_call() -> None:
    ki, _, sc = _index()
    assert ki.upload([]) == 0
    assert sc.uploaded == []


def test_keyword_search_maps_hits() -> None:
    hit = {
        "id": "k",
        "content": "c",
        "source": "regs.md",
        "section": "Rules",
        "access_tag": "public",
        "@search.score": 1.5,
    }
    ki, _, sc = _index([hit])
    hits = ki.keyword_search("overtaking", top=3, access_filter="access_tag eq 'public'")
    assert sc.searches[0] == {
        "search_text": "overtaking",
        "top": 3,
        "filter": "access_tag eq 'public'",
    }
    assert hits[0]["source"] == "regs.md" and hits[0]["score"] == 1.5


def test_vector_search_builds_query_and_maps_hits() -> None:
    hit = {"id": "k", "content": "c", "source": "regs.md", "section": None, "access_tag": "public"}
    ki, _, sc = _index([hit])
    hits = ki.vector_search([0.1, 0.2], top=2)
    call = sc.searches[0]
    assert call["search_text"] is None and call["top"] == 2
    assert len(call["vector_queries"]) == 1
    assert hits[0]["section"] is None and hits[0]["score"] is None


def test_default_clients_are_constructed(monkeypatch: pytest.MonkeyPatch) -> None:
    built: dict[str, Any] = {}

    def make_index_client(endpoint: str, credential: Any) -> FakeIndexClient:
        built["ic"] = (endpoint, credential)
        return FakeIndexClient()

    def make_search_client(endpoint: str, index: str, credential: Any) -> FakeSearchClient:
        built["sc"] = (endpoint, index, credential)
        return FakeSearchClient()

    monkeypatch.setattr(index_mod, "SearchIndexClient", make_index_client)
    monkeypatch.setattr(index_mod, "SearchClient", make_search_client)
    ki = KnowledgeIndex(CONFIG)
    ki.delete()  # exercises the default-constructed index client
    assert built["ic"][0] == CONFIG.endpoint
    assert built["sc"][1] == CONFIG.index
