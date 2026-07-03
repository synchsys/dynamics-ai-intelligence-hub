"""Schema-validated structured output from the model (#60, 8.3).

Requests JSON constrained to a Pydantic schema (Azure OpenAI ``json_schema``
response format), validates the reply with that schema, and — on a validation
failure — runs a bounded **repair** round that feeds the error back to the model
before giving up with a typed :class:`AIError`.

Built on :class:`~ai.client.AIClient`, so it inherits shared retry, structured
logging, and error translation. This is the reliable-JSON foundation for
function calling (#61), the CRM assistant, and the Paddock free-text intake
(#230).
"""

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, ValidationError

from ai.client import AIClient
from ai.exceptions import AIError
from shared.logging import get_logger

_logger = get_logger("ai.structured")


def _response_format(schema: type[BaseModel]) -> dict[str, Any]:
    """Azure OpenAI ``json_schema`` response format derived from a Pydantic model."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": schema.__name__,
            "schema": schema.model_json_schema(),
        },
    }


def _repair_message(schema: type[BaseModel], error: ValidationError) -> dict[str, str]:
    return {
        "role": "user",
        "content": (
            f"Your previous response did not match the required schema "
            f"'{schema.__name__}'. Validation errors:\n{error}\n"
            "Reply again with ONLY valid JSON that satisfies the schema."
        ),
    }


def structured_output[T: BaseModel](
    client: AIClient,
    messages: Sequence[Mapping[str, Any]],
    schema: type[T],
    *,
    max_repair: int = 1,
) -> T:
    """Return a ``schema`` instance parsed from the model's structured reply.

    Asks the model for ``json_schema``-constrained output and validates it with
    ``schema``. On a :class:`pydantic.ValidationError`, feeds the error back and
    retries up to ``max_repair`` times; if it still fails, raises
    :class:`AIError` (chained from the last validation error).
    """
    response_format = _response_format(schema)
    conversation: list[Mapping[str, Any]] = list(messages)
    last_error: ValidationError | None = None

    for attempt in range(max_repair + 1):
        content = client.chat(conversation, response_format=response_format)
        try:
            return schema.model_validate_json(content)
        except ValidationError as error:
            last_error = error
            _logger.warning(
                "structured output failed schema %s (attempt %d/%d)",
                schema.__name__,
                attempt + 1,
                max_repair + 1,
            )
            conversation = [
                *conversation,
                {"role": "assistant", "content": content},
                _repair_message(schema, error),
            ]

    raise AIError(
        f"structured output did not satisfy schema '{schema.__name__}' "
        f"after {max_repair + 1} attempt(s)"
    ) from last_error
