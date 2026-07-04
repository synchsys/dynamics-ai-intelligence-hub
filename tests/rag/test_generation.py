"""Tests for grounded generation — citations resolve to retrieved chunks."""

import json
from types import SimpleNamespace
from typing import Any

from ai import AIClient, AzureOpenAIConfig
from rag import Citation, RetrievedChunk, generate_answer

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="emb",
    api_key="k",
)

CHUNKS = [
    RetrievedChunk("regs.md#0", "DRS may be used in zones", "regs.md", "Overtaking", "public", 0.9),
    RetrievedChunk("regs.md#1", "hold position under SC", "regs.md", "Safety Car", "public", 0.7),
]


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


def _client(answer: str, citations: list[str]) -> tuple[AIClient, FakeSDK]:
    sdk = FakeSDK(json.dumps({"answer": answer, "citations": citations}))
    return AIClient(CONFIG, sdk=sdk, max_attempts=1, sleep=lambda _s: None), sdk


def test_answer_carries_resolved_citations() -> None:
    client, _ = _client("Use DRS in zones.", ["regs.md#0"])
    result = generate_answer(client, "when can I use DRS?", CHUNKS)
    assert result.answer == "Use DRS in zones."
    assert result.citations == [Citation("regs.md#0", "regs.md", "Overtaking")]
    assert result.is_grounded


def test_context_and_ids_are_passed_to_the_model() -> None:
    client, sdk = _client("ok", ["regs.md#0"])
    generate_answer(client, "q", CHUNKS)
    system = sdk.completions.calls[0]["messages"][0]["content"]
    assert "[regs.md#0]" in system and "DRS may be used in zones" in system


def test_hallucinated_citation_is_dropped() -> None:
    client, _ = _client("answer", ["regs.md#0", "made-up#9"])
    result = generate_answer(client, "q", CHUNKS)
    assert [c.id for c in result.citations] == ["regs.md#0"]  # unknown id filtered out


def test_duplicate_citations_are_deduped() -> None:
    client, _ = _client("answer", ["regs.md#0", "regs.md#0", "regs.md#1"])
    result = generate_answer(client, "q", CHUNKS)
    assert [c.id for c in result.citations] == ["regs.md#0", "regs.md#1"]


def test_no_chunks_returns_ungrounded_answer_without_calling_model() -> None:
    client, sdk = _client("unused", [])
    result = generate_answer(client, "q", [])
    assert not result.is_grounded and result.citations == []
    assert "don't have any sources" in result.answer
    assert sdk.completions.calls == []  # no model call when there is nothing to ground on


def test_empty_citations_means_not_grounded() -> None:
    client, _ = _client("The sources don't cover that.", [])
    result = generate_answer(client, "q", CHUNKS)
    assert result.citations == [] and not result.is_grounded
