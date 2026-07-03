"""Deterministically turn a :class:`WagerIntent` into validated grading parameters.

Resolves driver references to numbers, assembles the raw parameter dict for the
chosen settlement type, and validates it against that type's own Pydantic model
(``GRADERS[type][0]``). Any gap — unknown type, unresolved driver, missing
operator/number, schema-invalid params — raises :class:`MappingError` carrying
player-facing guidance, so intake rejects rather than guesses (ADR-0008).
"""

from pydantic import ValidationError

from openf1.models import Driver
from paddock.intake.schema import WagerIntent
from paddock.settlement.drivers import resolve_driver
from paddock.settlement.grading import GRADERS

# Settlement types that take only a single driver_number.
_DRIVER_ONLY = {
    "driver_wins",
    "podium_contains",
    "points_finish",
    "classified_finish",
    "driver_dnf",
    "beats_grid",
    "fastest_lap_by",
}


class MappingError(Exception):
    """Intake could not build valid parameters; ``guidance`` is player-facing."""

    def __init__(self, guidance: str) -> None:
        super().__init__(guidance)
        self.guidance = guidance


def _driver(intent: WagerIntent, drivers: list[Driver], *, which: str = "driver") -> int:
    reference = getattr(intent, which)
    if not reference:
        raise MappingError("Please name the driver your prediction is about.")
    number = resolve_driver(reference, drivers)
    if number is None:
        raise MappingError(
            f"I couldn't identify the driver '{reference}' in this session. "
            "Use a current driver's surname, three-letter code, or car number."
        )
    return number


def _int(intent: WagerIntent, *, unit: str) -> int:
    if intent.number is None:
        raise MappingError(f"This prediction needs a number ({unit}).")
    return int(intent.number)


def _operator(intent: WagerIntent) -> str:
    if intent.operator is None:
        raise MappingError("This prediction needs a comparison (e.g. 'fewer than', 'at least').")
    return intent.operator


def _raw_parameters(intent: WagerIntent, drivers: list[Driver], code: str) -> dict[str, object]:
    if code in _DRIVER_ONLY:
        return {"driver_number": _driver(intent, drivers)}
    if code == "head_to_head_finish":
        return {
            "driver_a": _driver(intent, drivers, which="driver"),
            "driver_b": _driver(intent, drivers, which="driver_b"),
        }
    if code == "driver_finish_position":
        return {
            "driver_number": _driver(intent, drivers),
            "operator": _operator(intent),
            "value": _int(intent, unit="finishing position"),
        }
    if code == "positions_gained_at_least":
        return {"driver_number": _driver(intent, drivers), "n": _int(intent, unit="positions")}
    if code == "pit_stops":
        return {
            "driver_number": _driver(intent, drivers),
            "operator": _operator(intent),
            "n": _int(intent, unit="pit stops"),
        }
    # winning_margin — no driver
    return {"operator": _operator(intent), "seconds": intent.number}


def map_parameters(intent: WagerIntent, drivers: list[Driver]) -> tuple[str, dict[str, object]]:
    """Return ``(settlement_type, validated_params)`` or raise :class:`MappingError`."""
    code = intent.settlement_type
    if code is None or code not in GRADERS:
        raise MappingError(f"'{code}' is not a prediction type I support.")
    if code == "winning_margin" and intent.number is None:
        raise MappingError("A winning-margin prediction needs a number of seconds.")

    raw = _raw_parameters(intent, drivers, code)
    model = GRADERS[code][0]
    try:
        validated = model.model_validate(raw)
    except ValidationError as error:
        raise MappingError(
            f"I understood the prediction as '{code}' but couldn't build valid parameters."
        ) from error
    return code, validated.model_dump(mode="json")
