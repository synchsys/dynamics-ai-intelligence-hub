"""Tests for the AI Request/Response Dataverse logging adapters."""

from typing import Any

from paddock.intake.logging_repo import DataversePromptLogger, NullLogger


class FakeUpserter:
    def __init__(self) -> None:
        self.upserts: list[tuple[str, str, dict[str, Any]]] = []

    def upsert(self, entity_set: str, alternate_key: str, data: Any) -> None:
        self.upserts.append((entity_set, alternate_key, dict(data)))


def test_dataverse_logger_writes_request_and_response() -> None:
    dv = FakeUpserter()
    logger = DataversePromptLogger(dv)
    logger.log_request("R1", purpose="wager-intake", model="gpt-5-mini", prompt="Sainz to win")
    logger.log_response(
        "R1",
        raw_output='{"x":1}',
        decision="propose",
        settlement_type="driver_wins",
        ok=True,
        error=None,
    )

    req = dv.upserts[0]
    assert req[0] == "racy_airequests"
    assert req[1] == "racy_requestcode='R1'"
    assert req[2]["racy_prompt"] == "Sainz to win"
    assert req[2]["racy_model"] == "gpt-5-mini"

    resp = dv.upserts[1]
    assert resp[0] == "racy_airesponses"
    assert resp[2]["racy_decision"] == "propose"
    assert resp[2]["racy_ok"] is True
    assert resp[2]["racy_settlementtypecode"] == "driver_wins"


def test_null_logger_is_a_noop() -> None:
    # Records nothing and never raises.
    logger = NullLogger()
    logger.log_request("R", purpose="p", model="m", prompt="x")
    logger.log_response("R", raw_output="", decision="d", settlement_type=None, ok=False, error="e")
