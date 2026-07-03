"""Tests for CrmAssistant — grounded answers, history, and logging."""

from types import SimpleNamespace
from typing import Any

from ai import AIClient, AzureOpenAIConfig
from ai.assistant import CrmAssistant

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="emb",
    api_key="k",
)


class _Completions:
    def __init__(self, answers: list[str]) -> None:
        self._answers = answers
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        text = self._answers[min(len(self.calls) - 1, len(self._answers) - 1)]
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=text, tool_calls=None))]
        )


class FakeSDK:
    def __init__(self, answers: list[str]) -> None:
        self.completions = _Completions(answers)
        self.chat = SimpleNamespace(completions=self.completions)


class FixedRetriever:
    def __init__(self, context: str) -> None:
        self._context = context

    def context(self, question: str) -> str:
        return self._context


class RecordingLogger:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []
        self.responses: list[dict[str, Any]] = []

    def log_request(self, request_code: str, *, purpose: str, model: str, prompt: str) -> None:
        self.requests.append(
            {"code": request_code, "purpose": purpose, "model": model, "prompt": prompt}
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
    ) -> None:
        self.responses.append(
            {"code": request_code, "raw": raw_output, "decision": decision, "ok": ok}
        )


def _assistant(
    answers: list[str], context: str = "Accounts:\n- name=Acme", logger: Any = None
) -> tuple[CrmAssistant, FakeSDK]:
    sdk = FakeSDK(answers)
    client = AIClient(CONFIG, sdk=sdk, max_attempts=1, sleep=lambda _s: None)
    assistant = (
        CrmAssistant(
            client=client,
            retriever=FixedRetriever(context),
            logger=logger,
            code_factory=lambda: "REQ-1",
        )
        if logger
        else CrmAssistant(
            client=client, retriever=FixedRetriever(context), code_factory=lambda: "REQ-1"
        )
    )
    return assistant, sdk


def test_answer_is_grounded_in_context() -> None:
    assistant, sdk = _assistant(["Acme is an account."])
    answer = assistant.ask("What accounts exist?")
    assert answer.text == "Acme is an account."
    assert "Acme" in answer.context
    # System message carries the retrieved context; user carries the question.
    messages = sdk.completions.calls[0]["messages"]
    assert messages[0]["role"] == "system" and "name=Acme" in messages[0]["content"]
    assert messages[-1] == {"role": "user", "content": "What accounts exist?"}


def test_conversation_history_is_carried_forward() -> None:
    assistant, sdk = _assistant(["First answer.", "Second answer."])
    assistant.ask("Q1")
    assistant.ask("Q2")
    second_messages = sdk.completions.calls[1]["messages"]
    # system, then prior (Q1 user + assistant answer), then Q2 user.
    roles = [m["role"] for m in second_messages]
    assert roles == ["system", "user", "assistant", "user"]
    assert second_messages[2]["content"] == "First answer."
    assert second_messages[-1]["content"] == "Q2"


def test_reset_clears_history() -> None:
    assistant, sdk = _assistant(["a", "b"])
    assistant.ask("Q1")
    assistant.reset()
    assistant.ask("Q2")
    assert [m["role"] for m in sdk.completions.calls[1]["messages"]] == ["system", "user"]


def test_logging_captures_request_and_response() -> None:
    logger = RecordingLogger()
    assistant, _ = _assistant(["Answered."], logger=logger)
    assistant.ask("What accounts exist?")
    assert logger.requests[0] == {
        "code": "REQ-1",
        "purpose": "crm-assistant",
        "model": "gpt-5-mini",
        "prompt": "What accounts exist?",
    }
    assert logger.responses[0]["decision"] == "answer"
    assert logger.responses[0]["raw"] == "Answered."
