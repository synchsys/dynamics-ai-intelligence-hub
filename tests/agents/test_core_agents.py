"""Unit tests for the four core agents in isolation (#76)."""

import json
from types import SimpleNamespace
from typing import Any

from agents import Planner, Reporter, Researcher, Reviewer
from ai import AIClient, AzureOpenAIConfig
from ai.tools import ToolRegistry, add_tool

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="emb",
    api_key="k",
)


class _Completions:
    def __init__(self, turns: list[SimpleNamespace]) -> None:
        self._turns = turns
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self._turns[len(self.calls) - 1]


class SDK:
    def __init__(self, turns: list[SimpleNamespace]) -> None:
        self.completions = _Completions(turns)
        self.chat = SimpleNamespace(completions=self.completions)


def _text(content: str) -> SimpleNamespace:
    msg = SimpleNamespace(content=content, tool_calls=None)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def _json(obj: Any) -> SimpleNamespace:
    return _text(json.dumps(obj))


def _tool_turn(cid: str, name: str, args: str) -> SimpleNamespace:
    call = SimpleNamespace(id=cid, function=SimpleNamespace(name=name, arguments=args))
    msg = SimpleNamespace(content=None, tool_calls=[call])
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def _client(turns: list[SimpleNamespace]) -> tuple[AIClient, SDK]:
    sdk = SDK(turns)
    return AIClient(CONFIG, sdk=sdk, max_attempts=1, sleep=lambda _s: None), sdk


# --- planner ----------------------------------------------------------------


def test_planner_returns_ordered_steps() -> None:
    client, sdk = _client([_json({"steps": ["find results", "summarise"]})])
    plan = Planner().plan(client, "analyse the Singapore GP")
    assert plan.steps == ["find results", "summarise"]
    assert "planner" in sdk.completions.calls[0]["messages"][0]["content"]


def test_planner_prompt_mentions_step_budget() -> None:
    client, sdk = _client([_json({"steps": ["a"]})])
    Planner(max_steps=3).plan(client, "goal")
    assert "3 steps" in sdk.completions.calls[0]["messages"][0]["content"]


# --- researcher -------------------------------------------------------------


def test_researcher_uses_tools_and_reports_findings() -> None:
    turns = [
        _tool_turn("c1", "add", '{"a": 2, "b": 3}'),
        _text("The sum of the figures is 5."),
    ]
    client, _ = _client(turns)
    registry = ToolRegistry()
    registry.register(add_tool())
    findings = Researcher(registry=registry).research(client, "add 2 and 3")
    assert findings == "The sum of the figures is 5."


def test_researcher_forwards_context() -> None:
    client, sdk = _client([_text("done")])
    Researcher().research(client, "task", context="planner said do X")
    assert "planner said do X" in sdk.completions.calls[0]["messages"][1]["content"]


# --- reviewer ---------------------------------------------------------------


def test_reviewer_returns_structured_verdict() -> None:
    client, _ = _client([_json({"approved": False, "issues": ["no citation"], "summary": "weak"})])
    review = Reviewer().review(client, "some draft answer", goal="answer accurately")
    assert review.approved is False
    assert review.issues == ["no citation"]
    assert review.summary == "weak"


def test_reviewer_includes_goal_in_prompt() -> None:
    client, sdk = _client([_json({"approved": True, "issues": [], "summary": "ok"})])
    Reviewer().review(client, "draft", goal="be correct")
    user_msg = sdk.completions.calls[0]["messages"][1]["content"]
    assert "be correct" in user_msg and "draft" in user_msg


# --- reporter ---------------------------------------------------------------


def test_reporter_writes_report_from_material() -> None:
    client, sdk = _client([_text("# Report\n\nEverything checks out.")])
    report = Reporter().report(client, "goal + findings + review")
    assert report.startswith("# Report")
    assert "reporter" in sdk.completions.calls[0]["messages"][0]["content"]
