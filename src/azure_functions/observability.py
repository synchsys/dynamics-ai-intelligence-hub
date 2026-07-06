"""Ingestion observability — structured logs + metrics + failure signal (#21).

Wraps an ingestion run to give it a run id, time it, emit custom metrics
(records, duration, failures), and log a structured start/complete/failure line
with context. On failure it emits the failure metric, logs, and **re-raises** so
the Function invocation fails and the Azure Monitor alert on failed runs fires
(see ``docs/architecture/observability.md``).

The metric sink is a Protocol so it's testable; ``LoggingMetricSink`` (default)
emits metrics as structured logs that Application Insights ingests as custom
metrics.
"""

import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from shared.logging import get_logger

_logger = get_logger("azure_functions.observability")


class MetricSink(Protocol):
    def emit(
        self, name: str, value: float, *, properties: Mapping[str, str] | None = None
    ) -> None: ...


class LoggingMetricSink:
    """Emits metrics as structured logs (Application Insights → customMetrics)."""

    def emit(self, name: str, value: float, *, properties: Mapping[str, str] | None = None) -> None:
        _logger.info("metric %s=%s %s", name, value, dict(properties or {}))


@dataclass(frozen=True)
class ObservabilityRecord:
    """Telemetry for one ingestion run."""

    run_id: str
    session_key: int
    duration_ms: float
    upserted: int
    settleable: bool
    outcome: str
    error: str | None = None


def observed_ingestion(
    session_key: int,
    run: Callable[[int], Mapping[str, Any]],
    *,
    metrics: MetricSink,
    run_id_factory: Callable[[], str] = lambda: uuid.uuid4().hex,
    clock: Callable[[], float] = time.perf_counter,
) -> ObservabilityRecord:
    """Run ``run(session_key)`` with timing, metrics, and structured logging.

    Returns a record on success; on any exception, emits the failure metric, logs
    with context, and re-raises so the invocation fails (and the alert fires).
    """
    run_id = run_id_factory()
    _logger.info("ingestion start run_id=%s session_key=%s", run_id, session_key)
    start = clock()
    try:
        summary = run(session_key)
    except Exception as error:
        duration_ms = round((clock() - start) * 1000, 1)
        metrics.emit("ingestion.failures", 1, properties={"run_id": run_id})
        metrics.emit(
            "ingestion.duration_ms", duration_ms, properties={"run_id": run_id, "outcome": "failed"}
        )
        _logger.error(
            "ingestion failed run_id=%s session_key=%s duration_ms=%s error=%s",
            run_id,
            session_key,
            duration_ms,
            error,
        )
        raise

    duration_ms = round((clock() - start) * 1000, 1)
    metrics.emit("ingestion.records", summary["upserted"], properties={"run_id": run_id})
    metrics.emit(
        "ingestion.duration_ms", duration_ms, properties={"run_id": run_id, "outcome": "success"}
    )
    record = ObservabilityRecord(
        run_id=run_id,
        session_key=session_key,
        duration_ms=duration_ms,
        upserted=int(summary["upserted"]),
        settleable=bool(summary["settleable"]),
        outcome="success",
    )
    _logger.info("ingestion complete %s", record)
    return record
