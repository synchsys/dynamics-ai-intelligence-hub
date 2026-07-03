"""A registry of tools the model can select from (#61)."""

from collections.abc import Iterator
from typing import Any

from ai.tools.base import Tool, UnknownToolError


class ToolRegistry:
    """Holds registered tools and dispatches validated model tool-calls to them."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool[Any]] = {}

    def register(self, tool: Tool[Any]) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool

    def __contains__(self, name: object) -> bool:
        return name in self._tools

    def __iter__(self) -> Iterator[Tool[Any]]:
        return iter(self._tools.values())

    def __len__(self) -> int:
        return len(self._tools)

    def openai_schema(self) -> list[dict[str, Any]]:
        """The ``tools=[...]`` payload advertising every registered tool."""
        return [tool.to_openai() for tool in self._tools.values()]

    def dispatch(self, name: str, raw_arguments: str | dict[str, Any] | None) -> Any:
        """Validate + run the named tool; raises :class:`UnknownToolError` if absent."""
        tool = self._tools.get(name)
        if tool is None:
            raise UnknownToolError(f"model requested unknown tool '{name}'")
        return tool.invoke(raw_arguments)
