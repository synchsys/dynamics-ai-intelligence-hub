"""Unit tests for the Dataverse client (mocked transport + fake credential)."""

from typing import Any

import httpx
import pytest
from azure.core.credentials import AccessToken

from api.client import RestClient
from dataverse import (
    DataverseAuthError,
    DataverseBatchError,
    DataverseClient,
    DataverseConfig,
    DataverseError,
    DataverseNotFoundError,
)
from shared.exceptions import ConfigError, ExternalServiceError

CONFIG = DataverseConfig(
    dataverse_url="https://org.crm.dynamics.com",
    tenant_id="tenant",
    client_id="client",
    client_secret="secret",
)
_GUID = "11111111-1111-1111-1111-111111111111"


class FakeCredential:
    def __init__(self, *, fail: bool = False) -> None:
        self._fail = fail

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        if self._fail:
            raise RuntimeError("auth boom")
        return AccessToken("fake-token", 9999999999)


def make_client(
    handler: object, *, credential: object | None = None, max_attempts: int = 2
) -> DataverseClient:
    rest = RestClient(
        CONFIG.api_base,
        transport=httpx.MockTransport(handler),  # type: ignore[arg-type]
        sleep=lambda _s: None,
        max_attempts=max_attempts,
    )
    return DataverseClient(
        CONFIG,
        credential=credential or FakeCredential(),  # type: ignore[arg-type]
        rest=rest,
    )


# --- config ----------------------------------------------------------------


def test_config_from_env_success() -> None:
    env = {
        "DATAVERSE_URL": "https://x.crm.dynamics.com/",
        "AZURE_TENANT_ID": "t",
        "AZURE_CLIENT_ID": "c",
        "AZURE_CLIENT_SECRET": "s",
    }
    cfg = DataverseConfig.from_env(env)
    assert cfg.dataverse_url == "https://x.crm.dynamics.com"  # trailing slash stripped
    assert cfg.scope == "https://x.crm.dynamics.com/.default"
    assert cfg.api_base == "https://x.crm.dynamics.com/api/data/v9.2"


def test_config_from_env_missing_raises() -> None:
    with pytest.raises(ConfigError, match="AZURE_CLIENT_SECRET"):
        DataverseConfig.from_env(
            {"DATAVERSE_URL": "https://x", "AZURE_TENANT_ID": "t", "AZURE_CLIENT_ID": "c"}
        )


# --- auth -------------------------------------------------------------------


def test_bearer_and_odata_headers_sent() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(request.headers)
        return httpx.Response(200, json={"value": []})

    make_client(handler).retrieve_multiple("contacts")
    assert seen["authorization"] == "Bearer fake-token"
    assert seen["odata-version"] == "4.0"


def test_auth_failure_raises_dataverse_auth_error() -> None:
    client = make_client(
        lambda r: httpx.Response(200, json={}), credential=FakeCredential(fail=True)
    )
    with pytest.raises(DataverseAuthError):
        client.retrieve_multiple("contacts")


# --- create/retrieve/update/delete -----------------------------------------


def test_create_returns_guid() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        entity_id = f"{CONFIG.api_base}/contacts({_GUID})"
        return httpx.Response(204, headers={"OData-EntityId": entity_id})

    assert make_client(handler).create("contacts", {"lastname": "Smith"}) == _GUID


def test_create_without_entity_id_raises() -> None:
    client = make_client(lambda r: httpx.Response(204))
    with pytest.raises(DataverseError, match="no entity id"):
        client.create("contacts", {"lastname": "Smith"})


def test_retrieve_returns_record() -> None:
    client = make_client(
        lambda r: httpx.Response(200, json={"contactid": _GUID, "lastname": "Smith"})
    )
    assert client.retrieve("contacts", _GUID)["lastname"] == "Smith"


def test_retrieve_passes_select() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["select"] = request.url.params.get("$select", "")
        return httpx.Response(200, json={"contactid": _GUID})

    make_client(handler).retrieve("contacts", _GUID, select=["lastname", "firstname"])
    assert seen["select"] == "lastname,firstname"


def test_retrieve_404_raises_not_found() -> None:
    client = make_client(lambda r: httpx.Response(404, text="nope"))
    with pytest.raises(DataverseNotFoundError):
        client.retrieve("contacts", _GUID)


def test_retrieve_multiple_single_page() -> None:
    client = make_client(lambda r: httpx.Response(200, json={"value": [{"a": 1}, {"a": 2}]}))
    assert client.retrieve_multiple("contacts", filter="a eq 1") == [{"a": 1}, {"a": 2}]


def test_retrieve_multiple_follows_nextlink() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "skiptoken" in str(request.url):
            return httpx.Response(200, json={"value": [{"p": 2}]})
        return httpx.Response(
            200,
            json={
                "value": [{"p": 1}],
                "@odata.nextLink": f"{CONFIG.api_base}/contacts?$skiptoken=x",
            },
        )

    assert make_client(handler).retrieve_multiple("contacts") == [{"p": 1}, {"p": 2}]


def test_retrieve_multiple_with_select_and_top() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["select"] = request.url.params.get("$select", "")
        seen["top"] = request.url.params.get("$top", "")
        return httpx.Response(200, json={"value": []})

    make_client(handler).retrieve_multiple("contacts", select=["a", "b"], top=5)
    assert seen["select"] == "a,b"
    assert seen["top"] == "5"


def test_update_sends_patch() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        return httpx.Response(204)

    make_client(handler).update("contacts", _GUID, {"lastname": "Jones"})
    assert seen["method"] == "PATCH"


def test_delete_sends_delete() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        return httpx.Response(204)

    make_client(handler).delete("contacts", _GUID)
    assert seen["method"] == "DELETE"


def test_upsert_patches_alternate_key() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["url"] = str(request.url)
        return httpx.Response(204)

    make_client(handler).upsert("contacts", "ref_code='ABC'", {"lastname": "Z"})
    assert seen["method"] == "PATCH"
    assert "ref_code=" in seen["url"]


def test_server_error_maps_to_dataverse_error() -> None:
    client = make_client(lambda r: httpx.Response(500, text="boom"), max_attempts=2)
    with pytest.raises(DataverseError):
        client.retrieve("contacts", _GUID)


# --- batch ------------------------------------------------------------------


def test_batch_create_success() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["ctype"] = request.headers["content-type"]
        captured["body"] = request.content.decode()
        return httpx.Response(200, text="HTTP/1.1 204 No Content")

    make_client(handler).batch_create("contacts", [{"lastname": "A"}, {"lastname": "B"}])
    assert captured["ctype"].startswith("multipart/mixed; boundary=batch_")
    assert "POST" in captured["body"]
    assert '"lastname": "A"' in captured["body"]


def test_batch_create_empty_is_noop() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200)

    make_client(handler).batch_create("contacts", [])
    assert calls["n"] == 0


def test_batch_create_failure_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="HTTP/1.1 400 Bad Request")

    with pytest.raises(DataverseBatchError):
        make_client(handler).batch_create("contacts", [{"lastname": "A"}])


def test_batch_upsert_atomic_changeset() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["ctype"] = request.headers["content-type"]
        captured["body"] = request.content.decode()
        return httpx.Response(200, text="HTTP/1.1 204 No Content")

    make_client(handler).batch_upsert(
        [
            ("racy_wagerslips", "racy_slipcode='S1'", {"racy_status": "Locked"}),
            ("racy_wallets", "racy_playercode='P1'", {"racy_balance": 20.0}),
        ]
    )
    assert captured["ctype"].startswith("multipart/mixed; boundary=batch_")
    assert "PATCH" in captured["body"]
    assert "racy_wagerslips(racy_slipcode='S1')" in captured["body"]
    assert "racy_wallets(racy_playercode='P1')" in captured["body"]


def test_batch_upsert_empty_is_noop() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200)

    make_client(handler).batch_upsert([])
    assert calls["n"] == 0


def test_batch_upsert_failure_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="HTTP/1.1 412 Precondition Failed")

    with pytest.raises(DataverseBatchError):
        make_client(handler).batch_upsert([("racy_wallets", "racy_playercode='P1'", {"x": 1})])


# --- lifecycle + hierarchy --------------------------------------------------


def test_context_manager_closes() -> None:
    with make_client(lambda r: httpx.Response(200, json={"value": []})) as client:
        assert client.retrieve_multiple("contacts") == []


def test_exception_hierarchy() -> None:
    for exc_type in (DataverseAuthError, DataverseNotFoundError, DataverseBatchError):
        assert issubclass(exc_type, DataverseError)
    assert issubclass(DataverseError, ExternalServiceError)
