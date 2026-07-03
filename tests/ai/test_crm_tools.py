"""Tests for guarded CRM action tools — read executes, write needs approval."""

from types import SimpleNamespace
from typing import Any

import pytest

from ai import AIClient, AzureOpenAIConfig
from ai.crm_tools import (
    ApprovalBroker,
    ApprovalError,
    build_crm_tools,
    create_followup_tool,
    lookup_tool,
)
from ai.tools import run_tools


class FakeReadGateway:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows
        self.last: dict[str, Any] = {}

    def retrieve_multiple(
        self, entity_set: str, *, filter: str | None = None, select: Any = None
    ) -> list[dict[str, Any]]:
        self.last = {"entity_set": entity_set, "filter": filter}
        return self._rows


class FakeWriteGateway:
    def __init__(self) -> None:
        self.created: list[tuple[str, dict[str, Any]]] = []

    def create(self, entity_set: str, data: dict[str, Any]) -> str:
        self.created.append((entity_set, data))
        return f"id-{len(self.created)}"


# --- read tool --------------------------------------------------------------


def test_lookup_tool_returns_records() -> None:
    gw = FakeReadGateway([{"name": "Acme"}, {"name": "Globex"}])
    result = lookup_tool(gw).invoke('{"entity_set": "accounts"}')
    assert result["count"] == 2
    assert result["records"][0]["name"] == "Acme"


def test_lookup_tool_caps_records() -> None:
    gw = FakeReadGateway([{"n": i} for i in range(50)])
    result = lookup_tool(gw, limit=5).invoke('{"entity_set": "accounts"}')
    assert result["count"] == 50 and len(result["records"]) == 5


# --- guarded write ----------------------------------------------------------


def test_write_tool_stages_and_does_not_execute() -> None:
    wg = FakeWriteGateway()
    broker = ApprovalBroker(wg, id_factory=lambda: "ACT-1")
    result = create_followup_tool(broker).invoke('{"subject": "Call Acme"}')
    assert result["status"] == "pending_approval"
    assert result["action_id"] == "ACT-1"
    assert wg.created == []  # nothing written yet
    assert len(broker.pending) == 1


def test_approval_executes_the_write() -> None:
    wg = FakeWriteGateway()
    broker = ApprovalBroker(wg, id_factory=lambda: "ACT-1")
    create_followup_tool(broker).invoke('{"subject": "Call Acme", "description": "Q4 renewal"}')
    record_id = broker.approve("ACT-1")

    assert record_id == "id-1"
    assert wg.created == [("tasks", {"subject": "Call Acme", "description": "Q4 renewal"})]
    assert broker.pending == []
    assert [e.event for e in broker.audit] == ["staged", "approved"]


def test_reject_discards_without_writing() -> None:
    wg = FakeWriteGateway()
    broker = ApprovalBroker(wg, id_factory=lambda: "ACT-1")
    create_followup_tool(broker).invoke('{"subject": "Call Acme"}')
    broker.reject("ACT-1")
    assert wg.created == []
    assert broker.pending == []
    assert [e.event for e in broker.audit] == ["staged", "rejected"]


def test_approve_unknown_action_raises() -> None:
    with pytest.raises(ApprovalError, match="no pending action 'nope'"):
        ApprovalBroker(FakeWriteGateway()).approve("nope")


def test_reject_unknown_action_raises() -> None:
    with pytest.raises(ApprovalError, match="no pending action 'nope'"):
        ApprovalBroker(FakeWriteGateway()).reject("nope")


def test_regarding_appears_in_summary() -> None:
    broker = ApprovalBroker(FakeWriteGateway(), id_factory=lambda: "A")
    create_followup_tool(broker).invoke('{"subject": "Call", "regarding": "Acme"}')
    assert "regarding Acme" in broker.pending[0].summary


# --- registry + run_tools integration ---------------------------------------

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


def test_build_crm_tools_registers_both() -> None:
    tools = build_crm_tools(FakeReadGateway([]), FakeWriteGateway())
    names = [t["function"]["name"] for t in tools.registry.openai_schema()]
    assert set(names) == {"lookup_records", "create_followup_activity"}


def test_model_looks_up_then_stages_write_via_loop() -> None:
    read_gw = FakeReadGateway([{"name": "Acme", "address1_city": "Cork"}])
    write_gw = FakeWriteGateway()
    tools = build_crm_tools(read_gw, write_gw, id_factory=lambda: "ACT-9")
    turns = [
        _turn(tool_calls=[_tool_call("c1", "lookup_records", '{"entity_set": "accounts"}')]),
        _turn(
            tool_calls=[_tool_call("c2", "create_followup_activity", '{"subject": "Call Acme"}')]
        ),
        _turn(content="I've queued a follow-up for approval."),
    ]
    client = AIClient(CONFIG, sdk=ScriptedSDK(turns), max_attempts=1, sleep=lambda _s: None)

    result = run_tools(client, [{"role": "user", "content": "follow up with Acme"}], tools.registry)
    assert "queued a follow-up" in result.content
    assert [c.name for c in result.calls] == ["lookup_records", "create_followup_activity"]
    # The write was staged, not executed, during the loop.
    assert write_gw.created == []
    assert len(tools.broker.pending) == 1
    # Human approves out-of-band -> now it executes.
    tools.broker.approve("ACT-9")
    assert write_gw.created == [("tasks", {"subject": "Call Acme"})]
