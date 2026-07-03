"""Tests for the Tool abstraction — schema emission + argument validation."""

import pytest
from pydantic import BaseModel

from ai.tools import Tool, ToolArgumentError
from ai.tools.samples import AddParams, add_tool


def test_to_openai_advertises_name_description_and_schema() -> None:
    schema = add_tool().to_openai()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "add"
    assert "Add two numbers" in schema["function"]["description"]
    assert set(schema["function"]["parameters"]["properties"]) == {"a", "b"}


def test_invoke_validates_and_runs_handler() -> None:
    assert add_tool().invoke('{"a": 2, "b": 3}') == 5.0


def test_invoke_accepts_decoded_dict() -> None:
    assert add_tool().invoke({"a": 1.5, "b": 2.5}) == 4.0


def test_invoke_none_arguments_uses_empty() -> None:
    class Empty(BaseModel):
        pass

    tool = Tool(name="noop", description="", params=Empty, handler=lambda _p: "ok")
    assert tool.invoke(None) == "ok"


def test_invoke_rejects_non_json_string() -> None:
    with pytest.raises(ToolArgumentError, match="non-JSON"):
        add_tool().invoke("not json")


def test_invoke_rejects_schema_invalid_args() -> None:
    with pytest.raises(ToolArgumentError, match="validation failed"):
        add_tool().invoke('{"a": "x", "b": 3}')


def test_add_params_model() -> None:
    assert AddParams(a=1, b=2).a == 1.0
