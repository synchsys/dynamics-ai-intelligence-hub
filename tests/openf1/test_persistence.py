"""Tests for OpenF1 → Dataverse persistence (mocked OpenF1 + fake Dataverse)."""

from collections.abc import Mapping, Sequence
from typing import Any

import httpx

from api.client import RestClient
from openf1 import MAPPINGS, OpenF1Client, OpenF1Persister, is_settleable
from openf1.persistence import _fmt_key_value, build_alternate_key, map_row

BASE = "https://api.test/v1"

# Canned OpenF1 rows keyed by endpoint path.
CANNED: dict[str, list[dict[str, Any]]] = {
    "/v1/drivers": [
        {"session_key": 9158, "driver_number": 1, "full_name": "A", "team_name": "T"},
        {"session_key": 9158, "driver_number": 44, "full_name": "B"},
    ],
    "/v1/session_result": [
        {"session_key": 9158, "driver_number": 1, "position": 1, "dnf": False},
        {"session_key": 9158, "driver_number": 44, "position": None, "dnf": True},
    ],
    "/v1/laps": [{"session_key": 9158, "driver_number": 1, "lap_number": 5, "lap_duration": 82.1}],
}


class FakeDataverse:
    """Records batch_upsert calls; satisfies SupportsBatchUpsert structurally."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Mapping[str, Any]]] = []  # flattened operations
        self.batches: list[Sequence[tuple[str, str, Mapping[str, Any]]]] = []  # per-batch

    def batch_upsert(self, operations: Sequence[tuple[str, str, Mapping[str, Any]]]) -> None:
        ops = list(operations)
        self.batches.append(ops)
        self.calls.extend(ops)


def make_persister(
    canned: dict[str, list[dict[str, Any]]] | None = None,
) -> tuple[OpenF1Persister, FakeDataverse]:
    rows = canned if canned is not None else CANNED

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=rows.get(request.url.path, []))

    client = OpenF1Client(
        rest=RestClient(BASE, transport=httpx.MockTransport(handler), sleep=lambda _s: None)
    )
    dv = FakeDataverse()
    return OpenF1Persister(client, dv), dv


# --- mapping helpers -------------------------------------------------------


def test_build_alternate_key_composite() -> None:
    em = MAPPINGS["session_result"]
    key = build_alternate_key(em, {"session_key": 9158, "driver_number": 44})
    assert key == "racy_sessionkey=9158,racy_drivernumber=44"


def test_map_row_drops_none_and_renames() -> None:
    em = MAPPINGS["session_result"]
    payload = map_row(em, {"session_key": 9158, "driver_number": 1, "position": None, "dnf": True})
    assert payload == {"racy_sessionkey": 9158, "racy_drivernumber": 1, "racy_dnf": True}
    assert "racy_position" not in payload  # None dropped


def test_fmt_key_value() -> None:
    assert _fmt_key_value(9158) == "9158"
    assert _fmt_key_value("2024-05-01") == "'2024-05-01'"
    assert _fmt_key_value(True) == "'True'"  # bool guarded before int


# --- persist_endpoint / ingest_session -------------------------------------


def test_persist_endpoint_upserts_each_row() -> None:
    persister, dv = make_persister()
    result = persister.persist_endpoint(MAPPINGS["drivers"], 9158)
    assert result.upserted == 2
    assert result.invalid == 0
    assert all(entity == "racy_drivers" for entity, _key, _data in dv.calls)
    assert dv.calls[0][1] == "racy_sessionkey=9158,racy_drivernumber=1"
    assert len(dv.batches) == 1  # 2 rows fit in one batch


def test_persist_endpoint_chunks_into_batches() -> None:
    # 250 driver rows with batch_size=100 -> 3 batches (100, 100, 50).
    rows = [{"session_key": 9158, "driver_number": n, "full_name": f"D{n}"} for n in range(1, 251)]
    persister, dv = make_persister({"/v1/drivers": rows})
    persister._batch_size = 100
    result = persister.persist_endpoint(MAPPINGS["drivers"], 9158)
    assert result.upserted == 250
    assert [len(b) for b in dv.batches] == [100, 100, 50]


def test_persist_endpoint_empty_makes_no_batch_call() -> None:
    persister, dv = make_persister({"/v1/drivers": []})
    result = persister.persist_endpoint(MAPPINGS["drivers"], 9158)
    assert result.upserted == 0 and dv.batches == []


def test_ingest_session_covers_all_endpoints() -> None:
    persister, dv = make_persister()
    summary = persister.ingest_session(9158)
    assert set(summary.endpoints) == set(MAPPINGS)
    # drivers (2) + session_result (2) + laps (1) have data; others empty
    assert summary.endpoints["drivers"].upserted == 2
    assert summary.endpoints["session_result"].upserted == 2
    assert summary.endpoints["laps"].upserted == 1
    assert summary.endpoints["weather"].upserted == 0
    assert summary.total_upserted == 5


def test_ingest_is_idempotent_shape() -> None:
    persister, dv = make_persister()
    persister.ingest_session(9158)
    first = len(dv.calls)
    persister.ingest_session(9158)
    # upsert is idempotent by nature: a re-run issues the same upserts, no extra creates
    assert len(dv.calls) == first * 2
    assert dv.calls[:first] == dv.calls[first:]


def test_invalid_rows_are_skipped_not_fatal() -> None:
    bad = {"/v1/drivers": [{"driver_number": 1}, {"session_key": 9158, "driver_number": 2}]}
    persister, dv = make_persister(bad)
    result = persister.persist_endpoint(MAPPINGS["drivers"], 9158)
    assert result.upserted == 1  # the valid one
    assert result.invalid == 1  # missing session_key


# --- settlement completeness -----------------------------------------------


def test_settleable_when_minimum_present() -> None:
    persister, _dv = make_persister()
    assert persister.ingest_session(9158).settleable is True


def test_not_settleable_without_session_result() -> None:
    canned = {"/v1/drivers": CANNED["/v1/drivers"]}  # no session_result
    persister, _dv = make_persister(canned)
    summary = persister.ingest_session(9158)
    assert summary.endpoints["session_result"].upserted == 0
    assert summary.settleable is False


def test_is_settleable_helper_matches_property() -> None:
    persister, _dv = make_persister()
    summary = persister.ingest_session(9158)
    assert is_settleable(summary) is summary.settleable is True
