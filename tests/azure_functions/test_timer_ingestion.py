"""Tests for the timer-triggered OpenF1 -> Dataverse ingestion (#20)."""

from datetime import UTC, datetime
from typing import Any

import pytest

import azure_functions.ingestion as ingestion_mod
from azure_functions.ingestion import (
    IngestionConfig,
    ingest_from_env,
    run_ingestion,
)
from shared.exceptions import ConfigError

NOW = datetime(2026, 7, 6, 12, 0, tzinfo=UTC)


class FakeSummary:
    total_upserted = 42
    settleable = True


class FakePersister:
    def __init__(self) -> None:
        self.sessions: list[int] = []

    def ingest_session(self, session_key: int) -> FakeSummary:
        self.sessions.append(session_key)
        return FakeSummary()


# --- config -----------------------------------------------------------------


def test_config_from_env() -> None:
    assert IngestionConfig.from_env({"INGEST_SESSION_KEY": "9165"}).session_key == 9165


def test_config_missing_raises() -> None:
    with pytest.raises(ConfigError, match="INGEST_SESSION_KEY"):
        IngestionConfig.from_env({})


# --- run_ingestion ----------------------------------------------------------


def test_run_ingestion_returns_summary() -> None:
    persister = FakePersister()
    result = run_ingestion(persister, 9165, NOW)
    assert persister.sessions == [9165]
    assert result == {
        "task": "openf1-ingestion",
        "at": "2026-07-06T12:00:00+00:00",
        "session_key": 9165,
        "upserted": 42,
        "settleable": True,
    }


# --- ingest_from_env (timer entrypoint) -------------------------------------


def test_ingest_from_env_wires_config_and_factory() -> None:
    persister = FakePersister()
    result = ingest_from_env(
        NOW, env={"INGEST_SESSION_KEY": "9165"}, persister_factory=lambda: persister
    )
    assert persister.sessions == [9165]
    # ingest_from_env now returns an observability record.
    assert result.session_key == 9165 and result.upserted == 42 and result.outcome == "success"


def test_build_persister_constructs_real_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    built: dict[str, Any] = {}

    def make_dv_client(cfg: Any) -> str:
        built["dv_cfg"] = cfg
        return "dv-client"

    def make_persister(f1: Any, dv: Any) -> str:
        built["persister"] = (f1, dv)
        return "persister"

    monkeypatch.setattr(
        ingestion_mod, "DataverseConfig", type("C", (), {"from_env": staticmethod(lambda: "cfg")})
    )
    monkeypatch.setattr(ingestion_mod, "DataverseClient", make_dv_client)
    monkeypatch.setattr(ingestion_mod, "OpenF1Client", lambda: "f1-client")
    monkeypatch.setattr(ingestion_mod, "OpenF1Persister", make_persister)

    ingestion_mod.build_persister()
    assert built["dv_cfg"] == "cfg"
    assert built["persister"] == ("f1-client", "dv-client")
