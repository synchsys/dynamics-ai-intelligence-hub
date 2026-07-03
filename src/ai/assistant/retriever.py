"""CRM context retrieval for the assistant (#63).

The assistant answers grounded in CRM data, so it needs a way to pull relevant
records and format them as a context block. :class:`CrmRetriever` is the
contract; :class:`DataverseCrmRetriever` reads a configured set of views from
the ``src/dataverse`` layer. Relevance here is deliberately simple (a bounded
set of records per view) — knowledge-grounded, cited retrieval is Epic 9's RAG
(#65), which slots in behind the same contract.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol


class CrmRetriever(Protocol):
    def context(self, question: str) -> str: ...


class ReadGateway(Protocol):
    def retrieve_multiple(
        self, entity_set: str, *, filter: str | None = ..., select: Sequence[str] | None = ...
    ) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class EntityView:
    """One CRM table to surface as context, with the fields to show."""

    entity_set: str
    label: str
    select: tuple[str, ...]


class DataverseCrmRetriever:
    """Formats a bounded set of records from configured views as a context block."""

    def __init__(
        self, gateway: ReadGateway, views: Sequence[EntityView], *, per_view: int = 20
    ) -> None:
        self._gw = gateway
        self._views = list(views)
        self._per_view = per_view

    def context(self, question: str) -> str:
        blocks: list[str] = []
        for view in self._views:
            rows = self._gw.retrieve_multiple(view.entity_set, select=list(view.select))
            lines = [self._format(row, view.select) for row in rows[: self._per_view]]
            body = "\n".join(f"- {line}" for line in lines) if lines else "- (none)"
            blocks.append(f"{view.label}:\n{body}")
        return "\n\n".join(blocks)

    @staticmethod
    def _format(row: dict[str, Any], select: tuple[str, ...]) -> str:
        return ", ".join(f"{field}={row.get(field)}" for field in select)
