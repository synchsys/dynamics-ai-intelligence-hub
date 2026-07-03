"""Core types for settlement: outcomes, operators and per-type parameter models.

Parameter models are Pydantic (consistent with ``openf1.models``) so the intake
layer's structured output validates against them before grading.
"""

import operator as _op
from collections.abc import Callable
from enum import StrEnum

from pydantic import BaseModel


class Outcome(StrEnum):
    """The result of grading a wager against ingested data."""

    WIN = "win"
    LOSE = "lose"
    VOID = "void"  # required data absent/ambiguous — refund, never guess


_OPS: dict[str, Callable[[float, float], bool]] = {
    "==": _op.eq,
    "!=": _op.ne,
    "<": _op.lt,
    "<=": _op.le,
    ">": _op.gt,
    ">=": _op.ge,
}


class Operator(StrEnum):
    """Comparison operators usable in settlement parameters."""

    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="

    def apply(self, a: float, b: float) -> bool:
        return _OPS[self.value](a, b)


# --- per-type parameter models ---------------------------------------------


class DriverParams(BaseModel):
    """A single driver (types 1, 2, 3, 6, 7, 8, 10)."""

    driver_number: int


class DriverThresholdParams(BaseModel):
    """Driver finishing position vs a threshold (type 4)."""

    driver_number: int
    operator: Operator
    value: int


class HeadToHeadParams(BaseModel):
    """Two drivers, higher classified wins (type 5)."""

    driver_a: int
    driver_b: int


class PositionsGainedParams(BaseModel):
    """At least N positions gained from grid to finish (type 9)."""

    driver_number: int
    n: int


class WinningMarginParams(BaseModel):
    """Winning margin (P2 gap to leader) vs a threshold in seconds (type 11)."""

    operator: Operator
    seconds: float


class PitStopParams(BaseModel):
    """A driver's pit-stop count vs a threshold (type 12)."""

    driver_number: int
    operator: Operator
    n: int
