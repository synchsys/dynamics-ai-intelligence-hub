"""Trigger logic for the Functions app (#10), kept out of the binding layer.

The Azure Functions bindings in ``function_app.py`` are thin — they delegate to
these pure functions so the behaviour is unit-testable without the Functions
runtime. Later epics wire real work in here (OpenF1 ingestion on the timer, #20;
AI/health on HTTP) without touching the bindings.
"""

from datetime import datetime
from typing import Any

from shared.logging import get_logger

_logger = get_logger("azure_functions")

SERVICE = "dynamics-ai-intelligence-hub"
VERSION = "0.1.0"


def health_payload() -> dict[str, Any]:
    """Body for the HTTP health check."""
    return {"status": "ok", "service": SERVICE, "version": VERSION}


def run_scheduled_ingestion(now: datetime) -> dict[str, Any]:
    """Placeholder for the timer-triggered ingestion (real ingestion arrives in #20)."""
    _logger.info("scheduled ingestion tick at %s (placeholder)", now.isoformat())
    return {"task": "scheduled-ingestion", "at": now.isoformat(), "ingested": 0}
