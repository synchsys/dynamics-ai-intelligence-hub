"""Tests for the Functions trigger logic (bindings-free)."""

from datetime import UTC, datetime

from azure_functions.handlers import (
    SERVICE,
    VERSION,
    health_payload,
    run_scheduled_ingestion,
)


def test_health_payload() -> None:
    payload = health_payload()
    assert payload == {"status": "ok", "service": SERVICE, "version": VERSION}


def test_run_scheduled_ingestion_placeholder() -> None:
    now = datetime(2026, 7, 6, 12, 0, tzinfo=UTC)
    result = run_scheduled_ingestion(now)
    assert result == {
        "task": "scheduled-ingestion",
        "at": "2026-07-06T12:00:00+00:00",
        "ingested": 0,
    }
