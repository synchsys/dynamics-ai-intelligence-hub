"""The single-model function-calling loop (#61, ADR-0006).

``run_tools`` drives one model through a bounded tool-use conversation: advertise
the registry's tools, and while the model asks to call tools, validate + dispatch
each, append the results, and re-invoke — until the model returns a final text
answer. Tool errors are fed back to the model as the tool result so it can
self-correct within the iteration budget, rather than crashing the loop.

This is the layer Epic 10's agents **reuse** for orchestration (ADR-0006); it
does not itself do multi-agent planning.
"""

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from ai.client import AIClient
from ai.tools.base import ToolError
from ai.tools.registry import ToolRegistry


@dataclass
class ToolCallRecord:
    """One tool invocation the model made during a run."""

    name: str
    arguments: str
    result: str
    ok: bool


@dataclass
class ToolRunResult:
    """The outcome of a :func:`run_tools` conversation."""

    content: str
    calls: list[ToolCallRecord] = field(default_factory=list)
    iterations: int = 0


def _to_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str)


def _assistant_turn(message: Any, tool_calls: Sequence[Any]) -> dict[str, Any]:
    """Rebuild the assistant tool-call message to append to the conversation."""
    return {
        "role": "assistant",
        "content": message.content or "",
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in tool_calls
        ],
    }


def run_tools(
    client: AIClient,
    messages: Sequence[Mapping[str, Any]],
    registry: ToolRegistry,
    *,
    max_iterations: int = 6,
) -> ToolRunResult:
    """Run the model with tool access until it returns a final answer.

    Raises :class:`ToolError` if the model keeps calling tools past
    ``max_iterations`` without producing a final response.
    """
    conversation: list[Mapping[str, Any]] = list(messages)
    schema = registry.openai_schema()
    calls: list[ToolCallRecord] = []

    for iteration in range(1, max_iterations + 1):
        response = client.complete(conversation, tools=schema)
        message = response.choices[0].message
        tool_calls = getattr(message, "tool_calls", None)

        if not tool_calls:
            return ToolRunResult(
                content=str(message.content or ""), calls=calls, iterations=iteration
            )

        conversation.append(_assistant_turn(message, tool_calls))
        for tc in tool_calls:
            try:
                result = registry.dispatch(tc.function.name, tc.function.arguments)
                content, ok = _to_content(result), True
            except ToolError as error:
                content, ok = f"ERROR: {error}", False  # fed back so the model can recover
            calls.append(
                ToolCallRecord(
                    name=tc.function.name, arguments=tc.function.arguments, result=content, ok=ok
                )
            )
            conversation.append({"role": "tool", "tool_call_id": tc.id, "content": content})

    raise ToolError(f"tool loop did not converge within {max_iterations} iterations")
