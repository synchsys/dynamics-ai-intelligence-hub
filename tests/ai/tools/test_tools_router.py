"""Tests for run_tools — the model-driven function-calling loop."""

from types import SimpleNamespace
from typing import Any

import pytest

from ai import AIClient, AzureOpenAIConfig
from ai.tools import ToolError, ToolRegistry, add_tool, run_tools

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="text-embedding-3-small",
    api_key="k",
)


def _tool_call(call_id: str, name: str, arguments: str) -> SimpleNamespace:
    return SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=arguments))


def _turn(*, content: str | None = None, tool_calls: list[Any] | None = None) -> SimpleNamespace:
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class ScriptedSDK:
    """Returns a scripted completion per successive create() call; records kwargs."""

    def __init__(self, turns: list[SimpleNamespace]) -> None:
        self._turns = turns
        self.calls: list[dict[str, Any]] = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self._turns[len(self.calls) - 1]


def _client(turns: list[SimpleNamespace]) -> tuple[AIClient, ScriptedSDK]:
    sdk = ScriptedSDK(turns)
    return AIClient(CONFIG, sdk=sdk, max_attempts=1, sleep=lambda _s: None), sdk


def _registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(add_tool())
    return reg


def test_model_calls_tool_then_answers() -> None:
    turns = [
        _turn(tool_calls=[_tool_call("c1", "add", '{"a": 2, "b": 3}')]),
        _turn(content="The sum is 5."),
    ]
    client, sdk = _client(turns)
    result = run_tools(client, [{"role": "user", "content": "add 2 and 3"}], _registry())

    assert result.content == "The sum is 5."
    assert result.iterations == 2
    assert len(result.calls) == 1
    assert result.calls[0].name == "add" and result.calls[0].ok
    assert result.calls[0].result == "5.0"
    # The tools schema was advertised to the model on the first call.
    assert sdk.calls[0]["tools"][0]["function"]["name"] == "add"
    # The tool result was fed back with the matching tool_call_id.
    fed_back = sdk.calls[1]["messages"][-1]
    assert fed_back["role"] == "tool" and fed_back["tool_call_id"] == "c1"


def test_no_tool_calls_returns_immediately() -> None:
    client, _ = _client([_turn(content="hello")])
    result = run_tools(client, [{"role": "user", "content": "hi"}], _registry())
    assert result.content == "hello"
    assert result.calls == []
    assert result.iterations == 1


def test_bad_args_error_is_fed_back_and_model_recovers() -> None:
    turns = [
        _turn(tool_calls=[_tool_call("c1", "add", '{"a": "oops", "b": 3}')]),  # invalid
        _turn(tool_calls=[_tool_call("c2", "add", '{"a": 2, "b": 3}')]),  # corrected
        _turn(content="done: 5"),
    ]
    client, sdk = _client(turns)
    result = run_tools(client, [{"role": "user", "content": "add"}], _registry())

    assert result.content == "done: 5"
    assert [c.ok for c in result.calls] == [False, True]
    assert result.calls[0].result.startswith("ERROR:")
    # The error was fed back to the model before the corrected call.
    assert sdk.calls[1]["messages"][-1]["content"].startswith("ERROR:")


def test_unknown_tool_error_is_fed_back() -> None:
    turns = [
        _turn(tool_calls=[_tool_call("c1", "ghost", "{}")]),
        _turn(content="sorry"),
    ]
    client, _ = _client(turns)
    result = run_tools(client, [{"role": "user", "content": "x"}], _registry())
    assert result.calls[0].ok is False
    assert "unknown tool" in result.calls[0].result


def test_string_tool_result_passed_through_verbatim() -> None:
    from pydantic import BaseModel

    from ai.tools import Tool

    class Empty(BaseModel):
        pass

    reg = ToolRegistry()
    reg.register(Tool(name="ping", description="", params=Empty, handler=lambda _p: "pong"))
    turns = [
        _turn(tool_calls=[_tool_call("c1", "ping", "{}")]),
        _turn(content="ok"),
    ]
    client, sdk = _client(turns)
    result = run_tools(client, [{"role": "user", "content": "ping"}], reg)
    assert result.calls[0].result == "pong"  # str result not JSON-encoded
    assert sdk.calls[1]["messages"][-1]["content"] == "pong"


def test_non_convergence_raises() -> None:
    # Model keeps calling tools forever; loop must stop at max_iterations.
    turns = [_turn(tool_calls=[_tool_call(f"c{i}", "add", '{"a": 1, "b": 1}')]) for i in range(5)]
    client, _ = _client(turns)
    with pytest.raises(ToolError, match="did not converge"):
        run_tools(client, [{"role": "user", "content": "loop"}], _registry(), max_iterations=3)
