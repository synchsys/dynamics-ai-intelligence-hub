"""Free-text wager intake (#230) — the LLM front door to the Paddock game.

Maps a punter's free text to a validated, priced :class:`DraftSlip` or a
guided rejection, logging prompt/response for governance.
"""

from paddock.intake.logging_repo import (
    DataversePromptLogger,
    NullLogger,
    PromptLogger,
)
from paddock.intake.mapping import MappingError, map_parameters
from paddock.intake.schema import SETTLEMENT_CODES, WagerIntent
from paddock.intake.service import DraftSlip, IntakeResult, WagerIntakeService

__all__ = [
    "WagerIntakeService",
    "IntakeResult",
    "DraftSlip",
    "WagerIntent",
    "SETTLEMENT_CODES",
    "map_parameters",
    "MappingError",
    "PromptLogger",
    "NullLogger",
    "DataversePromptLogger",
]
