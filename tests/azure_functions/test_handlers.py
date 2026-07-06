"""Tests for the Functions HTTP health logic (bindings-free)."""

from azure_functions.handlers import SERVICE, VERSION, health_payload


def test_health_payload() -> None:
    payload = health_payload()
    assert payload == {"status": "ok", "service": SERVICE, "version": VERSION}
