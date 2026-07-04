"""Tests for RAG grounding of the CRM assistant (#65) — grounded vs fallback."""

from collections.abc import Sequence
from dataclasses import dataclass, field
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


@dataclass
class FakeCitation:
    source: str
    section: str | None = None


@dataclass
class FakeCited:
    answer: str
    citations: list[FakeCitation]

    @property
    def is_grounded(self) -> bool:
        return bool(self.citations)


@dataclass
class FakeKnowledge:
    """A stand-in RAG assistant; records the roles it was asked with."""

    result: FakeCited
    asked_roles: list[Sequence[str]] = field(default_factory=list)

    def ask(self, question: str, roles: Sequence[str]) -> FakeCited:
        self.asked_roles.append(roles)
        return self.result


class RecordingRetriever:
    def __init__(self) -> None:
        self.calls = 0

    def context(self, question: str) -> str:
        self.calls += 1
        return "Accounts:\n- name=Acme"


class _Completions:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        msg = SimpleNamespace(content="CRM data answer.", tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


class FakeSDK:
    def __init__(self) -> None:
        self.completions = _Completions()
        self.chat = SimpleNamespace(completions=self.completions)


def _assistant(
    knowledge: Any, roles: Sequence[str] = ()
) -> tuple[CrmAssistant, RecordingRetriever, FakeSDK]:
    sdk = FakeSDK()
    client = AIClient(CONFIG, sdk=sdk, max_attempts=1, sleep=lambda _s: None)
    retriever = RecordingRetriever()
    assistant = CrmAssistant(client=client, retriever=retriever, knowledge=knowledge, roles=roles)
    return assistant, retriever, sdk


def test_grounded_knowledge_answer_is_returned_with_citations() -> None:
    knowledge = FakeKnowledge(FakeCited("DRS is used in zones.", [FakeCitation("regs.md", "DRS")]))
    assistant, retriever, sdk = _assistant(knowledge, roles=["manager"])

    answer = assistant.ask("when can I use DRS?")
    assert answer.text == "DRS is used in zones."
    assert answer.grounded_in == "knowledge"
    assert [c.source for c in answer.citations] == ["regs.md"]
    # Knowledge grounded, so the CRM data path is not touched.
    assert retriever.calls == 0
    assert sdk.completions.calls == []
    assert knowledge.asked_roles == [["manager"]]  # caller roles forwarded


def test_falls_back_to_crm_when_knowledge_ungrounded() -> None:
    knowledge = FakeKnowledge(FakeCited("no idea", []))  # is_grounded False
    assistant, retriever, sdk = _assistant(knowledge)

    answer = assistant.ask("who is Acme?")
    assert answer.text == "CRM data answer."
    assert answer.grounded_in == "crm"
    assert answer.citations == []
    assert retriever.calls == 1  # fell back to CRM retrieval + generation
    assert len(sdk.completions.calls) == 1


def test_no_knowledge_source_uses_crm_path() -> None:
    assistant, retriever, sdk = _assistant(None)
    answer = assistant.ask("who is Acme?")
    assert answer.grounded_in == "crm" and retriever.calls == 1


def test_logging_distinguishes_rag_from_crm() -> None:
    class RecordingLogger:
        def __init__(self) -> None:
            self.responses: list[str] = []

        def log_request(self, request_code: str, *, purpose: str, model: str, prompt: str) -> None:
            pass

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
            self.responses.append(decision)

    grounded = FakeKnowledge(FakeCited("cited", [FakeCitation("s")]))
    logger = RecordingLogger()
    a1, _, _ = _assistant(grounded)
    a1.logger = logger
    a1.ask("q")
    assert logger.responses == ["answer-rag"]
