"""Tests for the OpenF1 ingestion client (mocked transport, no network)."""

import httpx
import pytest

from api.client import RestClient
from api.exceptions import ApiStatusError
from openf1 import DEFAULT_BASE_URL, OpenF1Client

BASE = "https://api.test/v1"

# (method name, expected endpoint path)
ENDPOINTS = [
    ("get_meetings", "/meetings"),
    ("get_sessions", "/sessions"),
    ("get_drivers", "/drivers"),
    ("get_session_result", "/session_result"),
    ("get_starting_grid", "/starting_grid"),
    ("get_laps", "/laps"),
    ("get_pit", "/pit"),
    ("get_position", "/position"),
    ("get_stints", "/stints"),
    ("get_weather", "/weather"),
]


def make_client(handler: object, *, max_attempts: int = 2) -> OpenF1Client:
    rest = RestClient(
        BASE,
        transport=httpx.MockTransport(handler),  # type: ignore[arg-type]
        sleep=lambda _s: None,
        max_attempts=max_attempts,
    )
    return OpenF1Client(rest=rest)


# --- happy paths across every endpoint -------------------------------------


@pytest.mark.parametrize(("method", "path"), ENDPOINTS)
def test_endpoint_returns_list(method: str, path: str) -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        return httpx.Response(200, json=[{"ok": True}])

    result = getattr(make_client(handler), method)()
    assert result == [{"ok": True}]
    assert seen["path"] == f"/v1{path}"


@pytest.mark.parametrize(("method", "path"), ENDPOINTS)
def test_endpoint_logs(method: str, path: str, capsys: pytest.CaptureFixture[str]) -> None:
    from shared.logging import configure_logging

    configure_logging(json_output=False)
    client = make_client(lambda r: httpx.Response(200, json=[]))
    getattr(client, method)()
    assert path.strip("/") in capsys.readouterr().err


# --- filters ---------------------------------------------------------------


def test_single_filter_becomes_query_param() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["session_key"] = request.url.params.get("session_key", "")
        return httpx.Response(200, json=[])

    make_client(handler).get_laps(session_key=9158)
    assert seen["session_key"] == "9158"


def test_multiple_filters_combined() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["session_key"] = request.url.params.get("session_key", "")
        seen["driver_number"] = request.url.params.get("driver_number", "")
        return httpx.Response(200, json=[])

    make_client(handler).get_laps(session_key=9158, driver_number=1)
    assert seen["session_key"] == "9158"
    assert seen["driver_number"] == "1"


def test_qualifying_session_key_flows_through() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["session_key"] = request.url.params.get("session_key", "")
        return httpx.Response(200, json=[{"position": 1}])

    # A qualifying session key uses exactly the same method as a race one.
    assert make_client(handler).get_session_result(session_key=7700) == [{"position": 1}]
    assert seen["path"] == "/v1/session_result"
    assert seen["session_key"] == "7700"


def test_none_filters_are_dropped() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["has_dn"] = "driver_number" in request.url.params
        return httpx.Response(200, json=[])

    make_client(handler).get_drivers(session_key=1, driver_number=None)  # type: ignore[arg-type]
    assert seen["has_dn"] is False


def test_empty_result() -> None:
    assert make_client(lambda r: httpx.Response(200, json=[])).get_pit(session_key=1) == []


def test_non_list_payload_is_wrapped() -> None:
    result = make_client(lambda r: httpx.Response(200, json={"detail": "x"})).get_weather()
    assert result == [{"detail": "x"}]


# --- config / errors / resilience ------------------------------------------


def test_default_base_url() -> None:
    assert DEFAULT_BASE_URL == "https://api.openf1.org/v1"


def test_error_propagates_as_api_status_error() -> None:
    client = make_client(lambda r: httpx.Response(400, text="bad request"), max_attempts=1)
    with pytest.raises(ApiStatusError):
        client.get_sessions(session_key=1)


def test_404_no_results_returns_empty() -> None:
    # OpenF1 answers 404 "No results found" for an empty query — not a failure.
    client = make_client(
        lambda r: httpx.Response(404, json={"detail": "No results found."}), max_attempts=1
    )
    assert client.get_starting_grid(session_key=1) == []


def test_transient_error_retried_via_rest_client() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503)
        return httpx.Response(200, json=[{"ok": True}])

    assert make_client(handler, max_attempts=2).get_session_result(session_key=1) == [{"ok": True}]
    assert calls["n"] == 2


def test_context_manager_closes() -> None:
    with make_client(lambda r: httpx.Response(200, json=[])) as client:
        assert client.get_sessions() == []


# --- collect (query-chunked large imports) ---------------------------------


def test_collect_chunks_and_concatenates() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        dn = request.url.params.get("driver_number", "")
        seen.append(dn)
        return httpx.Response(200, json=[{"dn": dn}])

    result = make_client(handler).collect(
        "laps", over="driver_number", values=[1, 44], session_key=9158
    )
    assert seen == ["1", "44"]
    assert result == [{"dn": "1"}, {"dn": "44"}]


def test_collect_dedupes_values() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json=[])

    make_client(handler).collect("laps", over="driver_number", values=[1, 1, 2])
    assert calls["n"] == 2
