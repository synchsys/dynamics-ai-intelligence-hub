"""Tests for AI CRM summaries (#62) — injected RecordSource + scripted SDK."""

from types import SimpleNamespace
from typing import Any

import pytest

from ai import AIClient, AzureOpenAIConfig
from ai.exceptions import AIError
from ai.summaries import CrmSummariser, SummaryError

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="text-embedding-3-small",
    api_key="k",
)


class _Completions:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.text, tool_calls=None))],
            usage=SimpleNamespace(total_tokens=55),
        )


class FakeSDK:
    def __init__(self, text: str) -> None:
        self.completions = _Completions(text)
        self.chat = SimpleNamespace(completions=self.completions)


class FakeSource:
    """Returns canned rows; records the queries it was asked."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows
        self.queries: list[tuple[str, str | None]] = []

    def retrieve_multiple(
        self, entity_set: str, *, filter: str | None = None, **kw: Any
    ) -> list[dict[str, Any]]:
        self.queries.append((entity_set, filter))
        return self._rows


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
        self.requests.append({"purpose": purpose, "prompt": prompt, "user_id": user_id})

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
        self.responses.append({"decision": decision, "ok": ok, "tokens": tokens, "raw": raw_output})


def _summariser(
    text: str, rows: list[dict[str, Any]], logger: Any = None, **kw: Any
) -> tuple[CrmSummariser, FakeSDK]:
    sdk = FakeSDK(text)
    client = AIClient(CONFIG, sdk=sdk, max_attempts=1, sleep=lambda _s: None)
    kwargs = {"logger": logger} if logger else {}
    return (
        CrmSummariser(client, FakeSource(rows), code_factory=lambda: "REQ-1", **kwargs, **kw),
        sdk,
    )


ACCOUNT = {
    "name": "Apex Dynamics",
    "accountnumber": "ACC-0001",
    "address1_city": "Cork",
    "telephone1": "+353-1-5551234",
    "@odata.etag": "W/x",
    "accountid": None,
}


def test_summarise_account_returns_text_and_uses_prompt() -> None:
    s, sdk = _summariser("Apex Dynamics is a Cork-based account.", [ACCOUNT])
    result = s.summarise_account("ACC-0001")
    assert result.text == "Apex Dynamics is a Cork-based account."
    assert result.truncated is False and result.tokens == 55
    messages = sdk.completions.calls[0]["messages"]
    assert (
        "account" in messages[0]["content"] and "120" in messages[0]["content"]
    )  # record_type + max_words
    assert "Apex Dynamics" in messages[1]["content"] and "ACC-0001" in messages[1]["content"]
    assert "@odata.etag" not in messages[1]["content"]  # system/None fields dropped


def test_summarise_case_queries_custom_table() -> None:
    s, _ = _summariser(
        "Case is high priority.", [{"racy_casecode": "CASE-0007", "racy_title": "Outage"}]
    )
    result = s.summarise_case("CASE-0007")
    assert "high" in result.text
    assert s.source.queries == [("racy_cases", "racy_casecode eq 'CASE-0007'")]  # type: ignore[attr-defined]


def test_no_record_raises_summary_error() -> None:
    s, _ = _summariser("unused", [])
    with pytest.raises(SummaryError, match="no account matched"):
        s.summarise_account("ACC-9999")


def test_long_context_is_truncated() -> None:
    big = {"name": "X" * 9000}
    s, sdk = _summariser("summary", [big], max_context_chars=500)
    result = s.summarise_account("ACC-0001")
    assert result.truncated is True
    assert len(sdk.completions.calls[0]["messages"][1]["content"]) <= 520  # ~cap + template


def test_logging_captures_request_and_response() -> None:
    logger = RecordingLogger()
    s, _ = _summariser("A summary.", [ACCOUNT], logger=logger)
    s.summarise_account("ACC-0001", user_id="user@example.com")
    assert logger.requests[0]["purpose"] == "crm-summary"
    assert logger.requests[0]["user_id"] == "user@example.com"
    assert logger.responses[0] == {
        "decision": "summary",
        "ok": True,
        "tokens": 55,
        "raw": "A summary.",
    }


def test_model_error_is_logged_and_reraised() -> None:
    logger = RecordingLogger()
    s, _ = _summariser("unused", [ACCOUNT], logger=logger)

    def boom(*_a: Any, **_k: Any) -> Any:
        raise AIError("model down")

    s.client.complete = boom  # type: ignore[method-assign]
    with pytest.raises(AIError, match="model down"):
        s.summarise_account("ACC-0001")
    assert logger.responses[0]["decision"] == "error" and logger.responses[0]["ok"] is False
