"""Multi-agent workflow — planner → researcher → reviewer → reporter (#26 / #124).

The headline agentic deliverable: one orchestrated run that takes a goal, plans
steps, researches each (via the #61 tool layer — Dataverse reads and/or the
Epic 9 RAG assistant), reviews the findings, and reports. Tool use routes through
the registry (ADR-0006); writes are staged behind the human-approval gate (#64);
every agent step emits a telemetry event. Deterministic, bounded, and testable —
the custom orchestration chosen in ADR-0007.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from agents.planner import Plan, Planner
from agents.reporter import Reporter
from agents.researcher import Researcher
from agents.reviewer import Review, Reviewer
from ai.client import AIClient
from ai.crm_tools import ApprovalBroker, PendingWrite
from ai.tools.base import Tool
from shared.logging import get_logger

_logger = get_logger("agents.workflow")


@dataclass(frozen=True)
class TraceEvent:
    """One step in the workflow trace (telemetry)."""

    step: str
    agent: str
    summary: str


@dataclass(frozen=True)
class WorkflowResult:
    """The full outcome of a multi-agent run."""

    goal: str
    plan: Plan
    findings: list[str]
    review: Review
    report: str
    trace: list[TraceEvent]
    pending_writes: list[PendingWrite] = field(default_factory=list)


def _preview(text: str, limit: int = 80) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + "…"


@dataclass
class MultiAgentWorkflow:
    """Orchestrates the four core agents into a single, traced run."""

    client: AIClient
    planner: Planner = field(default_factory=Planner)
    researcher: Researcher = field(default_factory=Researcher)
    reviewer: Reviewer = field(default_factory=Reviewer)
    reporter: Reporter = field(default_factory=Reporter)
    broker: ApprovalBroker | None = None
    on_event: Callable[[TraceEvent], None] | None = None

    def run(self, goal: str) -> WorkflowResult:
        trace: list[TraceEvent] = []

        def emit(step: str, agent: str, summary: str) -> None:
            event = TraceEvent(step=step, agent=agent, summary=summary)
            trace.append(event)
            _logger.info("workflow step %s (%s): %s", step, agent, summary)
            if self.on_event is not None:
                self.on_event(event)

        plan = self.planner.plan(self.client, goal)
        emit("plan", "planner", f"{len(plan.steps)} step(s)")

        findings: list[str] = []
        for i, step in enumerate(plan.steps):
            context = "\n".join(findings) or None
            finding = self.researcher.research(self.client, step, context=context)
            findings.append(finding)
            emit(f"research[{i}]", "researcher", _preview(finding))

        combined = "\n".join(f"- {f}" for f in findings) or "(no findings)"
        review = self.reviewer.review(self.client, combined, goal=goal)
        emit("review", "reviewer", f"approved={review.approved}: {_preview(review.summary)}")

        material = (
            f"Goal: {goal}\n\nFindings:\n{combined}\n\n"
            f"Review: {review.summary} (approved={review.approved})"
        )
        report = self.reporter.report(self.client, material)
        emit("report", "reporter", _preview(report))

        pending = list(self.broker.pending) if self.broker is not None else []
        return WorkflowResult(
            goal=goal,
            plan=plan,
            findings=findings,
            review=review,
            report=report,
            trace=trace,
            pending_writes=pending,
        )


def knowledge_search_tool(rag: Any, roles: Sequence[str]) -> Tool[Any]:
    """A researcher tool that searches the Epic 9 RAG assistant for cited knowledge.

    Wraps ``rag.ask(query, roles)`` so the researcher is *backed by RAG* while
    still going through the single tool layer. ``roles`` are captured for the run
    so retrieval stays permission-aware (#72).
    """
    from pydantic import BaseModel, Field

    class KnowledgeQuery(BaseModel):
        query: str = Field(description="A focused knowledge question to look up")

    def handler(params: KnowledgeQuery) -> dict[str, Any]:
        answer = rag.ask(params.query, roles)
        return {
            "answer": answer.answer,
            "grounded": answer.is_grounded,
            "citations": [getattr(c, "source", str(c)) for c in answer.citations],
        }

    return Tool(
        name="search_knowledge",
        description="Search the knowledge base for a cited, permission-aware answer.",
        params=KnowledgeQuery,
        handler=handler,
    )
