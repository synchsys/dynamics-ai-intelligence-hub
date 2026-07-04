"""End-to-end tests for the multi-agent workflow (#26)."""

import json
from types import SimpleNamespace
from typing import Any

from agents import (
    MultiAgentWorkflow,
    Researcher,
    TraceEvent,
    knowledge_search_tool,
)
from ai import AIClient, AzureOpenAIConfig
from ai.crm_tools import build_crm_tools
from ai.tools import ToolRegistry, add_tool

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="emb",
    api_key="k",
)


def _text(content: str) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content, tool_calls=None))]
    )


def _json(obj: Any) -> SimpleNamespace:
    return _text(json.dumps(obj))


def _tool(cid: str, name: str, args: str) -> SimpleNamespace:
    call = SimpleNamespace(id=cid, function=SimpleNamespace(name=name, arguments=args))
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=None, tool_calls=[call]))]
    )


class SDK:
    def __init__(self, turns: list[SimpleNamespace]) -> None:
        self._turns = turns
        self.calls: list[dict[str, Any]] = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self._turns[len(self.calls) - 1]


def _client(turns: list[SimpleNamespace]) -> AIClient:
    return AIClient(CONFIG, sdk=SDK(turns), max_attempts=1, sleep=lambda _s: None)


def test_full_workflow_produces_a_report() -> None:
    client = _client(
        [
            _json({"steps": ["count the results", "summarise the field"]}),  # planner
            _text("There are 19 results."),  # researcher step 0
            _text("The field had 19 classified drivers."),  # researcher step 1
            _json({"approved": True, "issues": [], "summary": "accurate and grounded"}),  # reviewer
            _text("# Race Report\n\n19 drivers were classified."),  # reporter
        ]
    )
    result = MultiAgentWorkflow(client).run("Report on session 9165")

    assert result.plan.steps == ["count the results", "summarise the field"]
    assert len(result.findings) == 2 and "19 results" in result.findings[0]
    assert result.review.approved is True
    assert result.report.startswith("# Race Report")
    # Telemetry: one event per agent step.
    assert [e.step for e in result.trace] == [
        "plan",
        "research[0]",
        "research[1]",
        "review",
        "report",
    ]
    assert result.pending_writes == []


def test_telemetry_callback_receives_every_step() -> None:
    client = _client(
        [
            _json({"steps": ["one"]}),
            _text("found it"),
            _json({"approved": True, "issues": [], "summary": "ok"}),
            _text("report"),
        ]
    )
    seen: list[TraceEvent] = []
    result = MultiAgentWorkflow(client, on_event=seen.append).run("goal")
    assert seen == result.trace
    assert {e.agent for e in seen} == {"planner", "researcher", "reviewer", "reporter"}


def test_write_action_is_staged_pending_approval() -> None:
    read_gw = SimpleNamespace(retrieve_multiple=lambda *a, **k: [])
    write_calls: list[Any] = []

    def _create(entity_set: str, data: Any) -> str:
        write_calls.append((entity_set, data))
        return "id-1"

    write_gw = SimpleNamespace(create=_create)
    tools = build_crm_tools(read_gw, write_gw, id_factory=lambda: "ACT-1")

    client = _client(
        [
            _json({"steps": ["create a follow-up task"]}),  # planner
            _tool(
                "c1", "create_followup_activity", '{"subject": "Call the customer"}'
            ),  # research: write
            _text("I have queued a follow-up for approval."),  # research: final
            _json({"approved": True, "issues": [], "summary": "ok"}),  # reviewer
            _text("# Report\n\nA follow-up is pending approval."),  # reporter
        ]
    )
    workflow = MultiAgentWorkflow(
        client, researcher=Researcher(registry=tools.registry), broker=tools.broker
    )
    result = workflow.run("Follow up with the customer")

    # The write was staged, not executed — blocked pending human approval.
    assert write_calls == []
    assert len(result.pending_writes) == 1
    assert result.pending_writes[0].action_id == "ACT-1"
    # Approving out-of-band executes it.
    tools.broker.approve("ACT-1")
    assert write_calls == [("tasks", {"subject": "Call the customer"})]


def test_empty_plan_still_reports() -> None:
    client = _client(
        [
            _json({"steps": []}),  # planner: no steps
            _json({"approved": False, "issues": ["no findings"], "summary": "nothing to review"}),
            _text("# Report\n\nNo findings were gathered."),
        ]
    )
    result = MultiAgentWorkflow(client).run("impossible goal")
    assert result.findings == []
    assert "No findings" in result.report
    assert [e.step for e in result.trace] == ["plan", "review", "report"]


# --- knowledge_search_tool (RAG-backed researcher) --------------------------


def test_knowledge_search_tool_wraps_rag() -> None:
    class FakeCitation:
        source = "regs.md"

    class FakeAnswer:
        answer = "DRS is used in zones."
        is_grounded = True
        citations = [FakeCitation()]

    class FakeRag:
        def __init__(self) -> None:
            self.asked: list[Any] = []

        def ask(self, query: str, roles: Any) -> FakeAnswer:
            self.asked.append((query, list(roles)))
            return FakeAnswer()

    rag = FakeRag()
    tool = knowledge_search_tool(rag, roles=["employee"])
    result = tool.invoke('{"query": "when can I use DRS?"}')
    assert result["answer"] == "DRS is used in zones."
    assert result["grounded"] is True
    assert result["citations"] == ["regs.md"]
    assert rag.asked == [("when can I use DRS?", ["employee"])]  # roles captured for the run


def test_knowledge_tool_registers_in_a_registry() -> None:
    rag = SimpleNamespace(
        ask=lambda q, r: SimpleNamespace(answer="a", is_grounded=True, citations=[])
    )
    registry = ToolRegistry()
    registry.register(knowledge_search_tool(rag, roles=["guest"]))
    registry.register(add_tool())
    assert {t["function"]["name"] for t in registry.openai_schema()} == {"search_knowledge", "add"}
