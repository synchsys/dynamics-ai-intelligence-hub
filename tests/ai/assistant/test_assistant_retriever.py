"""Tests for DataverseCrmRetriever — context formatting from CRM views."""

from collections.abc import Sequence
from typing import Any

from ai.assistant import DataverseCrmRetriever, EntityView


class FakeGateway:
    def __init__(self, data: dict[str, list[dict[str, Any]]]) -> None:
        self._data = data
        self.calls: list[str] = []

    def retrieve_multiple(
        self, entity_set: str, *, filter: str | None = None, select: Sequence[str] | None = None
    ) -> list[dict[str, Any]]:
        self.calls.append(entity_set)
        return self._data.get(entity_set, [])


VIEWS = [
    EntityView("accounts", "Accounts", ("name", "city")),
    EntityView("contacts", "Contacts", ("fullname",)),
]


def test_context_formats_configured_views() -> None:
    gw = FakeGateway(
        {
            "accounts": [{"name": "Acme", "city": "Cork"}],
            "contacts": [{"fullname": "Jo Bloggs"}],
        }
    )
    context = DataverseCrmRetriever(gw, VIEWS).context("who is in Cork?")
    assert "Accounts:" in context
    assert "- name=Acme, city=Cork" in context
    assert "Contacts:" in context
    assert "- fullname=Jo Bloggs" in context
    assert gw.calls == ["accounts", "contacts"]


def test_empty_view_renders_none() -> None:
    context = DataverseCrmRetriever(FakeGateway({}), VIEWS).context("q")
    assert "Accounts:\n- (none)" in context


def test_per_view_cap_limits_rows() -> None:
    rows = [{"name": f"A{i}", "city": "X"} for i in range(50)]
    gw = FakeGateway({"accounts": rows})
    context = DataverseCrmRetriever(gw, [VIEWS[0]], per_view=3).context("q")
    assert context.count("- name=") == 3
