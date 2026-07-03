"""Read-only sample tools (#61).

Two illustrative tools: a pure, dependency-free one (``add``) and a factory that
wraps a read-only Dataverse query behind a structural :class:`ReadGateway`
Protocol — so the ``ai`` layer stays decoupled from ``dataverse`` and the tool
is trivially testable with a fake gateway.
"""

from collections.abc import Sequence
from typing import Any, Protocol

from pydantic import BaseModel, Field

from ai.tools.base import Tool


class AddParams(BaseModel):
    a: float = Field(description="First addend")
    b: float = Field(description="Second addend")


def add_tool() -> Tool[AddParams]:
    """A pure arithmetic tool — the minimal end-to-end function-calling demo."""

    def handler(p: AddParams) -> float:
        return p.a + p.b

    return Tool(
        name="add",
        description="Add two numbers and return the sum.",
        params=AddParams,
        handler=handler,
    )


class ReadGateway(Protocol):
    def retrieve_multiple(
        self, entity_set: str, *, filter: str | None = ..., select: Sequence[str] | None = ...
    ) -> list[dict[str, Any]]: ...


class CountParams(BaseModel):
    entity_set: str = Field(description="Dataverse entity set, e.g. 'racy_sessionresults'")
    filter: str | None = Field(default=None, description="Optional OData $filter expression")


def record_count_tool(gateway: ReadGateway) -> Tool[CountParams]:
    """A read-only tool that counts rows in a Dataverse table (optionally filtered)."""

    def handler(p: CountParams) -> dict[str, Any]:
        rows = gateway.retrieve_multiple(p.entity_set, filter=p.filter)
        return {"entity_set": p.entity_set, "count": len(rows)}

    return Tool(
        name="count_records",
        description="Count records in a Dataverse table, with an optional OData filter.",
        params=CountParams,
        handler=handler,
    )
