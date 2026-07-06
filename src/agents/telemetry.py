"""Agent telemetry sink — per-step traces to Application Insights (#78).

Each step of a multi-agent run emits one structured trace, correlated under a
single ``run_id``, carrying its timing and token cost. The sink is a Protocol so
the workflow stays testable; :class:`LoggingTelemetrySink` (the default) emits
each step as a structured log line that Application Insights ingests as a
``customEvent`` — the same "log → App Insights" approach as the ingestion
observability (#21, ``azure_functions.observability``). The schema aligns with
the Epic 11 (11.D) observability standard; see
``docs/architecture/agent-telemetry.md``.

The ``track_event(name, properties, measurements)`` shape mirrors the Azure
Monitor ``TelemetryClient.track_event`` API, so a live implementation backed by
``opencensus``/``azure-monitor`` drops in behind the same Protocol.
"""

from collections.abc import Mapping
from typing import Protocol

from shared.logging import get_logger

_logger = get_logger("agents.telemetry")


class TelemetrySink(Protocol):
    def track_event(
        self,
        name: str,
        *,
        properties: Mapping[str, str],
        measurements: Mapping[str, float],
    ) -> None: ...


class LoggingTelemetrySink:
    """Emits agent step traces as structured logs (App Insights → customEvents)."""

    def track_event(
        self,
        name: str,
        *,
        properties: Mapping[str, str],
        measurements: Mapping[str, float],
    ) -> None:
        _logger.info(
            "event %s props=%s measurements=%s", name, dict(properties), dict(measurements)
        )
