"""Trigger logic for the Functions app (#10), kept out of the binding layer.

The Azure Functions bindings in ``function_app.py`` are thin — they delegate here
(health) and to ``ingestion.py`` (the timer) so behaviour is unit-testable
without the Functions runtime.
"""

from typing import Any

SERVICE = "dynamics-ai-intelligence-hub"
VERSION = "0.1.0"


def health_payload() -> dict[str, Any]:
    """Body for the HTTP health check."""
    return {"status": "ok", "service": SERVICE, "version": VERSION}
