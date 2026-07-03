"""The structured-output schema the model fills for free-text wager intake (#230).

One flat schema because the 12 Tier-A types reduce to a small set of raw inputs:
a primary driver, an optional second driver (head-to-head), an operator, and a
number (finishing position / seconds / N). The model either **proposes** exactly
one settlement type or **declines** with a reason; deterministic code
(``intake.mapping``) then resolves drivers and validates the concrete parameters
against the type's own Pydantic model — the model never picks final parameters
unchecked.
"""

from typing import Literal

from pydantic import BaseModel, Field

from paddock.settlement.registry import SETTLEMENT_TYPES

# The supported settlement-type codes, sourced from the registry (no drift).
SETTLEMENT_CODES: tuple[str, ...] = tuple(meta.code for meta in SETTLEMENT_TYPES)

OperatorLiteral = Literal["==", "!=", "<", "<=", ">", ">="]


class WagerIntent(BaseModel):
    """The model's structured reading of a free-text prediction."""

    decision: Literal["propose", "decline"] = Field(
        description="'propose' if the text maps to a supported prediction, else 'decline'"
    )
    settlement_type: str | None = Field(
        default=None,
        description=f"the single supported type code; one of: {', '.join(SETTLEMENT_CODES)}",
    )
    driver: str | None = Field(default=None, description="primary driver: name, acronym, or number")
    driver_b: str | None = Field(
        default=None, description="second driver (only for head-to-head predictions)"
    )
    operator: OperatorLiteral | None = Field(
        default=None, description="comparison operator for threshold/margin/pit-stop types"
    )
    number: float | None = Field(
        default=None,
        description="numeric value: finishing position, winning-margin seconds, or N",
    )
    restated: str | None = Field(
        default=None, description="a concise restatement of the accepted prediction"
    )
    reason: str | None = Field(
        default=None, description="why the prediction was declined (only when declining)"
    )
