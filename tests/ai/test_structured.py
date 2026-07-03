"""Tests for structured_output — validation + bounded repair (injected FakeSDK)."""

from typing import Any

import pytest
from pydantic import BaseModel

from ai import AIClient, AIError, AzureOpenAIConfig, structured_output

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="text-embedding-3-small",
    api_key="k",
)


class Person(BaseModel):
    name: str
    age: int


def _resp(content: str) -> Any:
    from types import SimpleNamespace

    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


class _SequencedCompletions:
    """Returns a scripted content string per successive call; records kwargs."""

    def __init__(self, contents: list[str]) -> None:
        self._contents = contents
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        idx = min(len(self.calls) - 1, len(self._contents) - 1)
        return _resp(self._contents[idx])


class FakeSDK:
    def __init__(self, contents: list[str]) -> None:
        from types import SimpleNamespace

        self.completions = _SequencedCompletions(contents)
        self.chat = SimpleNamespace(completions=self.completions)


def _client(contents: list[str]) -> tuple[AIClient, FakeSDK]:
    sdk = FakeSDK(contents)
    return AIClient(CONFIG, sdk=sdk, max_attempts=1, sleep=lambda _s: None), sdk


def test_valid_output_parses_on_first_try() -> None:
    client, sdk = _client(['{"name": "Ada", "age": 36}'])
    person = structured_output(client, [{"role": "user", "content": "make a person"}], Person)
    assert person == Person(name="Ada", age=36)
    assert len(sdk.completions.calls) == 1


def test_response_format_carries_the_schema() -> None:
    client, sdk = _client(['{"name": "Ada", "age": 36}'])
    structured_output(client, [{"role": "user", "content": "x"}], Person)
    rf = sdk.completions.calls[0]["response_format"]
    assert rf["type"] == "json_schema"
    assert rf["json_schema"]["name"] == "Person"
    assert "properties" in rf["json_schema"]["schema"]


def test_invalid_then_repaired() -> None:
    # First reply violates the schema (age is not an int); repair round fixes it.
    client, sdk = _client(['{"name": "Ada", "age": "old"}', '{"name": "Ada", "age": 36}'])
    person = structured_output(
        client, [{"role": "user", "content": "make a person"}], Person, max_repair=1
    )
    assert person.age == 36
    assert len(sdk.completions.calls) == 2
    # The repair turn re-sends the prior (bad) assistant reply + a corrective user message.
    repair_messages = sdk.completions.calls[1]["messages"]
    assert repair_messages[-1]["role"] == "user"
    assert "did not match the required schema" in repair_messages[-1]["content"]


def test_persistent_invalid_raises_ai_error() -> None:
    client, sdk = _client(['{"name": "Ada"}'])  # missing required 'age', every time
    with pytest.raises(AIError, match="did not satisfy schema 'Person'"):
        structured_output(client, [{"role": "user", "content": "x"}], Person, max_repair=2)
    assert len(sdk.completions.calls) == 3  # initial + 2 repair attempts


def test_no_repair_budget_raises_immediately() -> None:
    client, sdk = _client(["not even json"])
    with pytest.raises(AIError):
        structured_output(client, [{"role": "user", "content": "x"}], Person, max_repair=0)
    assert len(sdk.completions.calls) == 1
