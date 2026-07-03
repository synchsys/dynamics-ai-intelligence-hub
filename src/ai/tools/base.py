"""The tool abstraction for model-driven function calling (#61).

A :class:`Tool` binds a name + description + a Pydantic parameter model to a
handler. The parameter model is the single source of truth for both the schema
advertised to the model (``to_openai``) and the **argument validation** applied
before the handler runs (``invoke``) — the model never reaches a handler with
unvalidated input.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from ai.exceptions import AIError


class ToolError(AIError):
    """Base error for the function-calling tool layer."""


class UnknownToolError(ToolError):
    """The model requested a tool that is not registered."""


class ToolArgumentError(ToolError):
    """The model's arguments failed the tool's parameter-schema validation."""


@dataclass(frozen=True)
class Tool[P: BaseModel]:
    """A callable the model may invoke, described by a Pydantic parameter model."""

    name: str
    description: str
    params: type[P]
    handler: Callable[[P], Any]

    def to_openai(self) -> dict[str, Any]:
        """The OpenAI ``tools`` entry advertising this tool to the model."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.params.model_json_schema(),
            },
        }

    def invoke(self, raw_arguments: str | dict[str, Any] | None) -> Any:
        """Validate ``raw_arguments`` against the schema, then run the handler.

        ``raw_arguments`` is the model's tool-call arguments — a JSON string (as
        Azure OpenAI returns) or an already-decoded dict. Raises
        :class:`ToolArgumentError` on malformed JSON or schema-invalid input,
        so a bad model call never reaches the handler.
        """
        try:
            data = (
                json.loads(raw_arguments)
                if isinstance(raw_arguments, str)
                else (raw_arguments or {})
            )
        except json.JSONDecodeError as error:
            raise ToolArgumentError(
                f"tool '{self.name}' got non-JSON arguments: {error}"
            ) from error
        try:
            parsed = self.params.model_validate(data)
        except ValidationError as error:
            raise ToolArgumentError(
                f"tool '{self.name}' argument validation failed: {error}"
            ) from error
        return self.handler(parsed)
