"""Guarded CRM action tools for the assistant (#64, 8.8).

Built on the #61 tool layer: a **read** tool that looks records up immediately,
and a **write** tool (create a follow-up activity) that is *guarded* — invoking
it never touches Dataverse directly; it **stages** a pending action that a human
must explicitly approve before it executes. Every staged / approved / rejected
action is recorded in an audit trail. This is the safe read→do step on top of
the read-only assistant (#63), and the concrete case of human-in-the-loop (#80).
"""

import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from pydantic import BaseModel, Field

from ai.tools import Tool, ToolError, ToolRegistry
from shared.logging import get_logger

_logger = get_logger("ai.crm_tools")


class ReadGateway(Protocol):
    def retrieve_multiple(
        self, entity_set: str, *, filter: str | None = ..., select: Sequence[str] | None = ...
    ) -> list[dict[str, Any]]: ...


class WriteGateway(Protocol):
    def create(self, entity_set: str, data: dict[str, Any]) -> str: ...


class ApprovalError(ToolError):
    """A staged action could not be approved/rejected (unknown or already resolved)."""


@dataclass(frozen=True)
class PendingWrite:
    """A write action staged for human approval."""

    action_id: str
    entity_set: str
    data: dict[str, Any]
    summary: str


@dataclass
class ActionEvent:
    """An audit-trail entry for a staged/approved/rejected action."""

    event: str  # staged | approved | rejected
    action_id: str
    summary: str


class ApprovalBroker:
    """Stages guarded writes and executes them only on explicit approval."""

    def __init__(
        self, gateway: WriteGateway, *, id_factory: Callable[[], str] | None = None
    ) -> None:
        self._gw = gateway
        self._id_factory = id_factory or (lambda: uuid.uuid4().hex)
        self._pending: dict[str, PendingWrite] = {}
        self.audit: list[ActionEvent] = []

    def stage(self, entity_set: str, data: dict[str, Any], *, summary: str) -> PendingWrite:
        action = PendingWrite(self._id_factory(), entity_set, data, summary)
        self._pending[action.action_id] = action
        self.audit.append(ActionEvent("staged", action.action_id, summary))
        _logger.info("staged write %s: %s", action.action_id, summary)
        return action

    @property
    def pending(self) -> list[PendingWrite]:
        return list(self._pending.values())

    def approve(self, action_id: str) -> str:
        """Execute the staged write and return the created record id."""
        action = self._pending.pop(action_id, None)
        if action is None:
            raise ApprovalError(f"no pending action '{action_id}' to approve")
        record_id = self._gw.create(action.entity_set, action.data)
        self.audit.append(ActionEvent("approved", action_id, action.summary))
        _logger.info("approved write %s -> %s", action_id, record_id)
        return record_id

    def reject(self, action_id: str) -> None:
        action = self._pending.pop(action_id, None)
        if action is None:
            raise ApprovalError(f"no pending action '{action_id}' to reject")
        self.audit.append(ActionEvent("rejected", action_id, action.summary))
        _logger.info("rejected write %s", action_id)


class LookupParams(BaseModel):
    entity_set: str = Field(description="Dataverse entity set, e.g. 'accounts'")
    filter: str | None = Field(default=None, description="Optional OData $filter")
    select: list[str] | None = Field(default=None, description="Optional fields to return")


def lookup_tool(gateway: ReadGateway, *, limit: int = 20) -> Tool[LookupParams]:
    """A read tool: look records up in a Dataverse table (bounded result)."""

    def handler(p: LookupParams) -> dict[str, Any]:
        rows = gateway.retrieve_multiple(p.entity_set, filter=p.filter, select=p.select)
        return {"entity_set": p.entity_set, "count": len(rows), "records": rows[:limit]}

    return Tool(
        name="lookup_records",
        description="Look up records in a CRM table, optionally filtered. Read-only.",
        params=LookupParams,
        handler=handler,
    )


class FollowupParams(BaseModel):
    subject: str = Field(description="Short subject line for the follow-up task")
    description: str | None = Field(default=None, description="Optional detail")
    regarding: str | None = Field(default=None, description="Account/contact name this concerns")


def create_followup_tool(broker: ApprovalBroker) -> Tool[FollowupParams]:
    """A guarded write tool: stage a follow-up activity for approval (does not execute)."""

    def handler(p: FollowupParams) -> dict[str, Any]:
        data: dict[str, Any] = {"subject": p.subject}
        if p.description:
            data["description"] = p.description
        detail = f" regarding {p.regarding}" if p.regarding else ""
        action = broker.stage("tasks", data, summary=f"Create follow-up '{p.subject}'{detail}")
        return {
            "status": "pending_approval",
            "action_id": action.action_id,
            "summary": action.summary,
            "note": "This write requires human approval before it executes.",
        }

    return Tool(
        name="create_followup_activity",
        description=(
            "Create a follow-up activity (task). This is a guarded write: it is "
            "staged for human approval and does NOT take effect until approved."
        ),
        params=FollowupParams,
        handler=handler,
    )


@dataclass
class CrmActionTools:
    """Bundle of the CRM tools plus the broker that gates their writes."""

    registry: ToolRegistry
    broker: ApprovalBroker = field(repr=False)


def build_crm_tools(
    read_gw: ReadGateway, write_gw: WriteGateway, **broker_kwargs: Any
) -> CrmActionTools:
    """Assemble a registry with the read + guarded-write tools and their broker."""
    broker = ApprovalBroker(write_gw, **broker_kwargs)
    registry = ToolRegistry()
    registry.register(lookup_tool(read_gw))
    registry.register(create_followup_tool(broker))
    return CrmActionTools(registry=registry, broker=broker)
