"""Tests for ToolRegistry — registration, schema, dispatch."""

import pytest

from ai.tools import ToolRegistry, UnknownToolError, add_tool


def _registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(add_tool())
    return reg


def test_register_and_membership() -> None:
    reg = _registry()
    assert "add" in reg
    assert len(reg) == 1
    assert [t.name for t in reg] == ["add"]


def test_duplicate_registration_raises() -> None:
    reg = _registry()
    with pytest.raises(ValueError, match="already registered"):
        reg.register(add_tool())


def test_openai_schema_lists_all_tools() -> None:
    schema = _registry().openai_schema()
    assert [t["function"]["name"] for t in schema] == ["add"]


def test_dispatch_runs_validated_tool() -> None:
    assert _registry().dispatch("add", '{"a": 4, "b": 6}') == 10.0


def test_dispatch_unknown_tool_raises() -> None:
    with pytest.raises(UnknownToolError, match="unknown tool 'nope'"):
        _registry().dispatch("nope", "{}")
