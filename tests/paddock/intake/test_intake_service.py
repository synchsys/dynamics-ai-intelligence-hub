"""Tests for WagerIntakeService — free text → draft slip or guided rejection."""

import json
from types import SimpleNamespace
from typing import Any

from ai import AIClient, AzureOpenAIConfig
from openf1.models import Driver
from paddock.intake import IntakeResult, WagerIntakeService
from paddock.intake.logging_repo import PromptLogger
from paddock.odds import Odds

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="emb",
    api_key="k",
)
DRIVERS = [
    Driver(session_key=9165, driver_number=55, full_name="Carlos Sainz", name_acronym="SAI"),
    Driver(session_key=9165, driver_number=4, full_name="Lando Norris", name_acronym="NOR"),
]
ODDS = Odds(
    probability=0.33, decimal_odds=3.0, fractional="2/1", line="2/1 against", source="heuristic"
)


class _Completions:
    def __init__(self, content: str) -> None:
        self._content = content
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self._content, tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeSDK:
    def __init__(self, content: str) -> None:
        self.completions = _Completions(content)
        self.chat = SimpleNamespace(completions=self.completions)


class FakePricer:
    def __init__(self) -> None:
        self.priced: list[tuple[str, dict[str, Any]]] = []

    def price(self, settlement_type: str, parameters: Any) -> Odds:
        self.priced.append((settlement_type, dict(parameters)))
        return ODDS


class RecordingLogger:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []
        self.responses: list[dict[str, Any]] = []

    def log_request(
        self,
        request_code: str,
        *,
        purpose: str,
        model: str,
        prompt: str,
        user_id: str | None = None,
    ) -> None:
        self.requests.append(
            {
                "code": request_code,
                "purpose": purpose,
                "model": model,
                "prompt": prompt,
                "user_id": user_id,
            }
        )

    def log_response(
        self,
        request_code: str,
        *,
        raw_output: str,
        decision: str,
        settlement_type: str | None = None,
        ok: bool = True,
        error: str | None = None,
        tokens: int | None = None,
        latency_ms: float | None = None,
    ) -> None:
        self.responses.append(
            {
                "code": request_code,
                "decision": decision,
                "type": settlement_type,
                "ok": ok,
                "error": error,
                "latency_ms": latency_ms,
            }
        )


def _service(
    intent: dict[str, Any], logger: PromptLogger | None = None
) -> tuple[WagerIntakeService, FakePricer, FakeSDK]:
    sdk = FakeSDK(json.dumps(intent))
    client = AIClient(CONFIG, sdk=sdk, max_attempts=1, sleep=lambda _s: None)
    pricer = FakePricer()
    service = WagerIntakeService(client, pricer, logger=logger, code_factory=lambda: "REQ-TEST")
    return service, pricer, sdk


def _run(intent: dict[str, Any], logger: PromptLogger | None = None) -> IntakeResult:
    service, _pricer, _sdk = _service(intent, logger)
    return service.intake("some prediction", session_key=9165, drivers=DRIVERS)


def test_propose_produces_priced_draft_slip() -> None:
    result = _run(
        {
            "decision": "propose",
            "settlement_type": "driver_wins",
            "driver": "Sainz",
            "restated": "Carlos Sainz wins the session",
        }
    )
    assert result.accepted and result.slip is not None
    slip = result.slip
    assert slip.settlement_type == "driver_wins"
    assert slip.parameters == {"driver_number": 55}
    assert slip.odds.line == "2/1 against"
    assert slip.restated_text == "Carlos Sainz wins the session"
    assert slip.session_key == 9165


def test_decline_returns_guided_rejection() -> None:
    result = _run({"decision": "decline", "reason": "That's a weather bet, not a race outcome."})
    assert not result.accepted and result.guidance is not None
    assert "weather bet" in result.guidance
    assert "podium" in result.guidance.lower()  # supported-kinds list appended


def test_unresolved_driver_rejected_with_guidance() -> None:
    result = _run({"decision": "propose", "settlement_type": "driver_wins", "driver": "Nobody"})
    assert not result.accepted and result.guidance is not None
    assert "couldn't identify" in result.guidance


def test_missing_number_rejected() -> None:
    result = _run(
        {"decision": "propose", "settlement_type": "positions_gained_at_least", "driver": "Sainz"}
    )
    assert not result.accepted and result.guidance is not None
    assert "needs a number" in result.guidance


def test_malformed_model_output_is_safely_rejected() -> None:
    # 'banana' is not a valid decision; structured_output exhausts repair -> AIError.
    result = _run({"decision": "banana"})
    assert not result.accepted and result.guidance is not None
    assert "couldn't understand" in result.guidance


def test_logging_captures_request_and_response() -> None:
    logger = RecordingLogger()
    _run({"decision": "propose", "settlement_type": "driver_wins", "driver": "Sainz"}, logger)
    assert logger.requests[0] == {
        "code": "REQ-TEST",
        "purpose": "wager-intake",
        "model": "gpt-5-mini",
        "prompt": "some prediction",
        "user_id": None,
    }
    assert logger.responses[0]["decision"] == "propose"
    assert logger.responses[0]["ok"] is True
    assert logger.responses[0]["type"] == "driver_wins"
    # Every response path records a measured latency for observability.
    assert logger.responses[0]["latency_ms"] is not None and logger.responses[0]["latency_ms"] >= 0


def test_logging_records_acting_user() -> None:
    logger = RecordingLogger()
    service, _, _ = _service(
        {"decision": "propose", "settlement_type": "driver_wins", "driver": "Sainz"}, logger
    )
    service.intake(
        "some prediction", session_key=9165, drivers=DRIVERS, user_id="player@example.com"
    )
    assert logger.requests[0]["user_id"] == "player@example.com"


def test_logging_records_error_on_malformed() -> None:
    logger = RecordingLogger()
    _run({"decision": "banana"}, logger)
    assert logger.responses[0]["decision"] == "error"
    assert logger.responses[0]["ok"] is False


def test_logging_records_mapping_failure() -> None:
    logger = RecordingLogger()
    _run({"decision": "propose", "settlement_type": "driver_wins", "driver": "Nobody"}, logger)
    resp = logger.responses[0]
    assert resp["decision"] == "propose" and resp["ok"] is False and resp["error"]
