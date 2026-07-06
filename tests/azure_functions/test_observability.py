"""Tests for ingestion observability (#21)."""

from collections.abc import Mapping
from typing import Any

import pytest

from azure_functions.observability import (
    LoggingMetricSink,
    ObservabilityRecord,
    observed_ingestion,
)


class RecordingSink:
    def __init__(self) -> None:
        self.metrics: list[tuple[str, float, dict[str, str]]] = []

    def emit(self, name: str, value: float, *, properties: Mapping[str, str] | None = None) -> None:
        self.metrics.append((name, value, dict(properties or {})))


def _clock() -> Any:
    # Two readings 0.25s apart -> 250 ms duration.
    values = iter([1.0, 1.25])
    return lambda: next(values)


def test_success_records_and_emits_metrics() -> None:
    sink = RecordingSink()
    record = observed_ingestion(
        9165,
        lambda _sk: {"upserted": 42, "settleable": True},
        metrics=sink,
        run_id_factory=lambda: "RUN-1",
        clock=_clock(),
    )
    assert record == ObservabilityRecord(
        run_id="RUN-1",
        session_key=9165,
        duration_ms=250.0,
        upserted=42,
        settleable=True,
        outcome="success",
    )
    names = {m[0] for m in sink.metrics}
    assert names == {"ingestion.records", "ingestion.duration_ms"}
    records_metric = next(m for m in sink.metrics if m[0] == "ingestion.records")
    assert records_metric[1] == 42 and records_metric[2]["run_id"] == "RUN-1"


def test_failure_emits_failure_metric_and_reraises() -> None:
    sink = RecordingSink()

    def boom(_sk: int) -> dict[str, Any]:
        raise RuntimeError("dataverse down")

    with pytest.raises(RuntimeError, match="dataverse down"):
        observed_ingestion(9165, boom, metrics=sink, run_id_factory=lambda: "RUN-2", clock=_clock())
    names = {m[0] for m in sink.metrics}
    assert "ingestion.failures" in names  # failure metric emitted before re-raise
    failure = next(m for m in sink.metrics if m[0] == "ingestion.failures")
    assert failure[1] == 1 and failure[2]["run_id"] == "RUN-2"


def test_logging_metric_sink_emits_without_error() -> None:
    LoggingMetricSink().emit("ingestion.records", 5, properties={"run_id": "x"})
    LoggingMetricSink().emit("ingestion.duration_ms", 12.5)  # properties optional
