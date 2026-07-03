"""Tests for the sample tools (pure add + Dataverse record-count via fake gateway)."""

from collections.abc import Sequence
from typing import Any

from ai.tools import add_tool, record_count_tool


def test_add_tool_handler() -> None:
    assert add_tool().invoke('{"a": 40, "b": 2}') == 42.0


class FakeGateway:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows
        self.last_call: dict[str, Any] = {}

    def retrieve_multiple(
        self, entity_set: str, *, filter: str | None = None, select: Sequence[str] | None = None
    ) -> list[dict[str, Any]]:
        self.last_call = {"entity_set": entity_set, "filter": filter}
        return self._rows


def test_record_count_tool_counts_rows() -> None:
    gw = FakeGateway([{"x": 1}, {"x": 2}, {"x": 3}])
    result = record_count_tool(gw).invoke('{"entity_set": "racy_sessionresults"}')
    assert result == {"entity_set": "racy_sessionresults", "count": 3}
    assert gw.last_call == {"entity_set": "racy_sessionresults", "filter": None}


def test_record_count_tool_passes_filter() -> None:
    gw = FakeGateway([{"x": 1}])
    record_count_tool(gw).invoke(
        '{"entity_set": "racy_sessionresults", "filter": "racy_sessionkey eq 9165"}'
    )
    assert gw.last_call["filter"] == "racy_sessionkey eq 9165"
