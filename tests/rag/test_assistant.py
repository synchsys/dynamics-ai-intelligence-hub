"""End-to-end tests for the RAG assistant — role-filtered, cited, logged."""

import json
import re
from types import SimpleNamespace
from typing import Any

from ai import AIClient, AzureOpenAIConfig
from rag import RagAssistant, Retriever

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="emb",
    api_key="k",
)

DOCS: list[dict[str, Any]] = [
    {
        "id": "1",
        "content": "public canteen hours",
        "source": "policy.md",
        "section": "Canteen",
        "access_tag": "public",
    },
    {
        "id": "2",
        "content": "internal reorg memo",
        "source": "policy.md",
        "section": "Reorg",
        "access_tag": "internal",
    },
    {
        "id": "3",
        "content": "confidential M&A target",
        "source": "policy.md",
        "section": "M&A",
        "access_tag": "confidential",
    },
]


class FilterRespectingIndex:
    """Enforces the OData security filter like the real service."""

    def hybrid_search(
        self, query_text: str, vector: Any, *, top: int = 5, access_filter: str | None = None
    ) -> list[dict[str, Any]]:
        if not access_filter:
            allowed = {d["access_tag"] for d in DOCS}
        else:
            m = re.search(r"search\.in\(access_tag, '([^']*)', ','\)", access_filter)
            allowed = set(m.group(1).split(",")) if m else set()
        return [d for d in DOCS if d["access_tag"] in allowed][:top]


class StubEmbedder:
    def embed(self, texts: Any) -> list[list[float]]:
        return [[0.0] for _ in texts]


class _Completions:
    def __init__(self, content: str) -> None:
        self._content = content
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        msg = SimpleNamespace(content=self._content, tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


class FakeSDK:
    def __init__(self, content: str) -> None:
        self.completions = _Completions(content)
        self.chat = SimpleNamespace(completions=self.completions)


class RecordingLogger:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []
        self.responses: list[dict[str, Any]] = []

    def log_request(self, request_code: str, *, purpose: str, model: str, prompt: str) -> None:
        self.requests.append({"code": request_code, "purpose": purpose, "prompt": prompt})

    def log_response(
        self,
        request_code: str,
        *,
        raw_output: str,
        decision: str,
        settlement_type: str | None = None,
        ok: bool = True,
        error: str | None = None,
    ) -> None:
        self.responses.append({"ok": ok, "error": error, "decision": decision})


def _assistant(citations: list[str], logger: Any = None) -> tuple[RagAssistant, FakeSDK]:
    sdk = FakeSDK(json.dumps({"answer": "Here is what the sources say.", "citations": citations}))
    client = AIClient(CONFIG, sdk=sdk, max_attempts=1, sleep=lambda _s: None)
    retriever = Retriever(FilterRespectingIndex(), StubEmbedder())  # type: ignore[arg-type]
    assistant = (
        RagAssistant(retriever=retriever, client=client, logger=logger, code_factory=lambda: "REQ")
        if logger
        else RagAssistant(retriever=retriever, client=client, code_factory=lambda: "REQ")
    )
    return assistant, sdk


def test_manager_gets_cited_answer_across_all_levels() -> None:
    assistant, _ = _assistant(["1", "3"])
    answer = assistant.ask("what are the company plans?", ["manager"])
    assert answer.is_grounded
    assert {c.id for c in answer.citations} == {"1", "3"}
    assert any(c.section == "M&A" for c in answer.citations)


def test_guest_answer_cannot_cite_confidential_even_if_model_tries() -> None:
    # The model 'cites' the confidential doc, but the guest never retrieved it,
    # so it is dropped — the two-user access guarantee holds end to end.
    assistant, _ = _assistant(["1", "3"])
    answer = assistant.ask("what are the company plans?", ["guest"])
    ids = {c.id for c in answer.citations}
    assert ids == {"1"}
    assert "3" not in ids  # confidential never leaks to a guest


def test_two_users_get_different_result_sets() -> None:
    guest, _ = _assistant(["1", "3"])
    manager, _ = _assistant(["1", "3"])
    guest_ids = {c.id for c in guest.ask("q", ["guest"]).citations}
    manager_ids = {c.id for c in manager.ask("q", ["manager"]).citations}
    assert "3" in manager_ids and "3" not in guest_ids


def test_unknown_role_gets_no_sources_and_no_model_call() -> None:
    assistant, sdk = _assistant(["1"])
    answer = assistant.ask("q", ["intruder"])
    assert not answer.is_grounded and answer.citations == []
    assert sdk.completions.calls == []  # deny-by-default -> nothing retrieved -> no generation


def test_prompt_and_response_are_logged() -> None:
    logger = RecordingLogger()
    _assistant(["1"], logger)[0].ask("hello?", ["guest"])
    assert logger.requests[0]["purpose"] == "rag-assistant"
    assert logger.requests[0]["prompt"] == "hello?"
    assert logger.responses[0]["decision"] == "answer" and logger.responses[0]["ok"] is True


def test_logs_error_when_no_permitted_sources() -> None:
    logger = RecordingLogger()
    _assistant(["1"], logger)[0].ask("q", ["intruder"])
    assert logger.responses[0]["ok"] is False
    assert logger.responses[0]["error"] == "no permitted sources retrieved"
