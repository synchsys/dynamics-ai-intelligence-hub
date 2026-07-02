"""Tests for the reusable REST client (mocked transport, no network)."""

import httpx
import pytest

from api import (
    ApiConnectionError,
    ApiError,
    ApiStatusError,
    ApiTimeoutError,
    RestClient,
)
from api.client import _is_transient
from shared.exceptions import ExternalServiceError


def _noop_sleep(_seconds: float) -> None:
    return None


def make_client(handler: httpx.MockTransport | object, **kwargs: object) -> RestClient:
    transport = httpx.MockTransport(handler)  # type: ignore[arg-type]
    return RestClient(
        "https://api.test",
        transport=transport,
        sleep=_noop_sleep,
        **kwargs,  # type: ignore[arg-type]
    )


# --- happy paths -----------------------------------------------------------


def test_get_returns_response() -> None:
    client = make_client(lambda req: httpx.Response(200, json={"ok": True}))
    resp = client.get("/thing")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_post_sends_json_body() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["content"] = request.content.decode()
        return httpx.Response(201, json={"id": 1})

    client = make_client(handler)
    resp = client.post("/items", json={"name": "x"})
    assert resp.status_code == 201
    assert seen["method"] == "POST"
    assert '"name"' in str(seen["content"])


def test_request_generic_method() -> None:
    client = make_client(lambda req: httpx.Response(200, text=req.method))
    assert client.request("DELETE", "/x").text == "DELETE"


def test_base_url_joins_path() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=str(request.url))

    client = make_client(handler)
    assert client.get("/a/b").text == "https://api.test/a/b"


def test_custom_headers_sent() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=request.headers.get("x-api-key", ""))

    transport = httpx.MockTransport(handler)
    client = RestClient(
        "https://api.test", headers={"X-Api-Key": "secret"}, transport=transport, sleep=_noop_sleep
    )
    assert client.get("/x").text == "secret"


# --- error mapping ---------------------------------------------------------


def test_404_raises_status_error_and_is_not_retried() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(404, text="missing")

    client = make_client(handler)
    with pytest.raises(ApiStatusError) as info:
        client.get("/missing")
    assert info.value.status_code == 404
    assert info.value.body == "missing"
    assert calls["n"] == 1  # 4xx is permanent


def test_400_not_retried() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(400)

    client = make_client(handler, max_attempts=4)
    with pytest.raises(ApiStatusError):
        client.get("/bad")
    assert calls["n"] == 1


def test_timeout_maps_to_api_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("slow", request=request)

    client = make_client(handler, max_attempts=1)
    with pytest.raises(ApiTimeoutError):
        client.get("/slow")


def test_connect_error_maps_to_connection_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    client = make_client(handler, max_attempts=1)
    with pytest.raises(ApiConnectionError):
        client.get("/down")


# --- retry behaviour (via the shared decorator) ----------------------------


def test_5xx_retried_then_succeeds() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(503)
        return httpx.Response(200, text="recovered")

    client = make_client(handler, max_attempts=3)
    assert client.get("/flaky").text == "recovered"
    assert calls["n"] == 3


def test_5xx_exhausts_retries() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(500)

    client = make_client(handler, max_attempts=3)
    with pytest.raises(ApiStatusError) as info:
        client.get("/down")
    assert info.value.status_code == 500
    assert calls["n"] == 3


def test_429_is_retried() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429)
        return httpx.Response(200)

    client = make_client(handler, max_attempts=2)
    assert client.get("/limited").status_code == 200
    assert calls["n"] == 2


def test_connection_error_is_retried_then_succeeds() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.ConnectError("blip", request=request)
        return httpx.Response(200, text="ok")

    client = make_client(handler, max_attempts=2)
    assert client.get("/x").text == "ok"
    assert calls["n"] == 2


# --- _is_transient predicate ----------------------------------------------


@pytest.mark.parametrize("status", [429, 500, 502, 503])
def test_transient_statuses(status: int) -> None:
    assert _is_transient(ApiStatusError(status, "")) is True


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
def test_permanent_statuses(status: int) -> None:
    assert _is_transient(ApiStatusError(status, "")) is False


def test_transient_connection_and_timeout() -> None:
    assert _is_transient(ApiConnectionError("x")) is True
    assert _is_transient(ApiTimeoutError("x")) is True


def test_unknown_exception_not_transient() -> None:
    assert _is_transient(ValueError("x")) is False


# --- lifecycle + hierarchy -------------------------------------------------


def test_context_manager_closes() -> None:
    with make_client(lambda req: httpx.Response(200)) as client:
        assert client.get("/x").status_code == 200


def test_close_is_idempotent() -> None:
    client = make_client(lambda req: httpx.Response(200))
    client.close()
    client.close()


def test_exceptions_are_external_service_errors() -> None:
    for exc_type in (ApiError, ApiConnectionError, ApiTimeoutError):
        assert issubclass(exc_type, ExternalServiceError)
    assert issubclass(ApiStatusError, ApiError)


def test_request_logs(capsys: pytest.CaptureFixture[str]) -> None:
    from shared.logging import configure_logging

    configure_logging(json_output=False)
    client = make_client(lambda req: httpx.Response(200))
    client.get("/logged")
    assert "GET /logged" in capsys.readouterr().err
