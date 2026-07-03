"""Settlement Capability Registry and deterministic grading (Tier A, types 1–12).

Public API: grade free-text-derived specs deterministically over ingested
OpenF1 data. Consumed by the settlement engine (#229), intake (#230) and odds
pricing (#227).
"""

from paddock.settlement.context import GradingContext, is_classified
from paddock.settlement.drivers import resolve_driver
from paddock.settlement.grading import GRADERS, grade
from paddock.settlement.registry import (
    SETTLEMENT_TYPES,
    SettlementTypeMeta,
    seed,
)
from paddock.settlement.types import (
    DriverParams,
    DriverThresholdParams,
    HeadToHeadParams,
    Operator,
    Outcome,
    PitStopParams,
    PositionsGainedParams,
    WinningMarginParams,
)

__all__ = [
    "Outcome",
    "Operator",
    "grade",
    "GRADERS",
    "GradingContext",
    "is_classified",
    "resolve_driver",
    "SETTLEMENT_TYPES",
    "SettlementTypeMeta",
    "seed",
    "DriverParams",
    "DriverThresholdParams",
    "HeadToHeadParams",
    "PositionsGainedParams",
    "WinningMarginParams",
    "PitStopParams",
]
