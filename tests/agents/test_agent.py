"""Proof for ADR-0007: a single Agent calling one tool via the #61 layer."""

from types import SimpleNamespace
from typing import Any

from agents import Agent, agent_with_tools
from ai import AIClient, AzureOpenAIConfig
from ai.tools import add_tool

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="emb",
    api_key="k",
)


def _tool_call(cid: str, name: str, args: str) -> SimpleNamespace:
    return SimpleNamespace(id=cid, function=SimpleNamespace(name=name, arguments=args))


def _turn(*, content: str | None = None, tool_calls: Any = None) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content, tool_calls=tool_calls))]
    )


class ScriptedSDK:
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


def test_single_agent_calls_one_tool() -> None:
    turns = [
        _turn(tool_calls=[_tool_call("c1", "add", '{"a": 2, "b": 3}')]),
        _turn(content="The total is 5."),
    ]
    client, sdk = _client(turns)
    agent = agent_with_tools("calculator", "You add numbers on request.", [add_tool()])

    result = agent.run(client, "please add 2 and 3")
    assert result.content == "The total is 5."
    assert [c.name for c in result.calls] == ["add"]
    assert result.calls[0].result == "5.0"
    # The agent's role instructions are the system message.
    assert "calculator agent" in sdk.calls[0]["messages"][0]["content"]


def test_agent_forwards_context_as_a_message() -> None:
    client, sdk = _client([_turn(content="done")])
    agent = Agent("reporter", "You summarise findings.")
    agent.run(client, "write the report", context="researcher found X")
    roles = [m["role"] for m in sdk.calls[0]["messages"]]
    assert roles == ["system", "user", "user"]
    assert "researcher found X" in sdk.calls[0]["messages"][1]["content"]


def test_agent_without_context_has_no_extra_message() -> None:
    client, sdk = _client([_turn(content="ok")])
    Agent("planner", "You plan.").run(client, "plan the work")
    assert [m["role"] for m in sdk.calls[0]["messages"]] == ["system", "user"]


def test_agent_defaults_to_empty_registry() -> None:
    assert len(Agent("solo", "just answer").registry) == 0
