"""Multi-agent workflow — planner → researcher → reviewer → reporter (#26 / #124).

The headline agentic deliverable: one orchestrated run that takes a goal, plans
steps, researches each (via the #61 tool layer — Dataverse reads and/or the
Epic 9 RAG assistant), reviews the findings, and reports. Tool use routes through
the registry (ADR-0006); writes are staged behind the human-approval gate (#64);
every agent step emits a telemetry event. Deterministic, bounded, and testable —
the custom orchestration chosen in ADR-0007.
"""

import time
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from agents.planner import Plan, Planner
from agents.reporter import Reporter
from agents.researcher import Researcher
from agents.reviewer import Review, Reviewer
from agents.telemetry import LoggingTelemetrySink, TelemetrySink
from ai.client import AIClient
from ai.crm_tools import ApprovalBroker, PendingWrite
from ai.tools.base import Tool
from shared.logging import get_logger

_logger = get_logger("agents.workflow")

# App Insights customEvent name for a single agent step (11.D-aligned schema).
STEP_EVENT = "agent.step"


@dataclass(frozen=True)
class TraceEvent:
    """One step in the workflow trace, correlated under ``run_id`` (telemetry, #78)."""

    run_id: str
    sequence: int
    step: str
    agent: str
    summary: str
    duration_ms: float
    tokens: int | None = None


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
    telemetry: TelemetrySink = field(default_factory=LoggingTelemetrySink)
    run_id_factory: Callable[[], str] = field(default_factory=lambda: (lambda: uuid.uuid4().hex))
    clock: Callable[[], float] = time.perf_counter

    def run(self, goal: str) -> WorkflowResult:
        run_id = self.run_id_factory()
        trace: list[TraceEvent] = []
        sequence = 0
        _logger.info("workflow start run_id=%s goal=%s", run_id, _preview(goal))

        # Meter tokens per step: every completion funnels through AIClient.complete,
        # which fires on_usage, so a running total lets each step report its delta.
        tokens_seen = 0

        def _accumulate(total: int | None) -> None:
            nonlocal tokens_seen
            if total is not None:
                tokens_seen += total

        def record(step: str, agent: str, summary: str, duration_ms: float, tokens: int) -> None:
            nonlocal sequence
            event = TraceEvent(
                run_id=run_id,
                sequence=sequence,
                step=step,
                agent=agent,
                summary=summary,
                duration_ms=round(duration_ms, 1),
                tokens=tokens if tokens > 0 else None,
            )
            sequence += 1
            trace.append(event)
            _logger.info(
                "workflow step %s run_id=%s (%s) %sms tokens=%s: %s",
                step,
                run_id,
                agent,
                event.duration_ms,
                event.tokens,
                summary,
            )
            self.telemetry.track_event(
                STEP_EVENT,
                properties={
                    "run_id": run_id,
                    "sequence": str(event.sequence),
                    "step": step,
                    "agent": agent,
                },
                measurements={
                    "duration_ms": event.duration_ms,
                    "tokens": float(event.tokens or 0),
                },
            )
            if self.on_event is not None:
                self.on_event(event)

        previous_hook = self.client.on_usage
        self.client.on_usage = _accumulate
        try:
            start, before = self.clock(), tokens_seen
            plan = self.planner.plan(self.client, goal)
            record(
                "plan",
                "planner",
                f"{len(plan.steps)} step(s)",
                (self.clock() - start) * 1000,
                tokens_seen - before,
            )

            findings: list[str] = []
            for i, step in enumerate(plan.steps):
                context = "\n".join(findings) or None
                start, before = self.clock(), tokens_seen
                finding = self.researcher.research(self.client, step, context=context)
                findings.append(finding)
                record(
                    f"research[{i}]",
                    "researcher",
                    _preview(finding),
                    (self.clock() - start) * 1000,
                    tokens_seen - before,
                )

            combined = "\n".join(f"- {f}" for f in findings) or "(no findings)"
            start, before = self.clock(), tokens_seen
            review = self.reviewer.review(self.client, combined, goal=goal)
            record(
                "review",
                "reviewer",
                f"approved={review.approved}: {_preview(review.summary)}",
                (self.clock() - start) * 1000,
                tokens_seen - before,
            )

            material = (
                f"Goal: {goal}\n\nFindings:\n{combined}\n\n"
                f"Review: {review.summary} (approved={review.approved})"
            )
            start, before = self.clock(), tokens_seen
            report = self.reporter.report(self.client, material)
            record(
                "report",
                "reporter",
                _preview(report),
                (self.clock() - start) * 1000,
                tokens_seen - before,
            )
        finally:
            self.client.on_usage = previous_hook

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
