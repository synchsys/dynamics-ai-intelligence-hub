"""Settlement Capability Registry — reference-data metadata + seeding.

The registry names the Tier-A settlement types the system can grade, their
labels and parameter fields. ``seed`` upserts them into the Dataverse
``racy_settlementtypes`` reference table (created with the Paddock schema, #225).
Parameter fields are derived from the grading param models so metadata can't
drift from the code.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from paddock.settlement.grading import GRADERS

_LABELS: dict[str, str] = {
    "driver_wins": "Driver wins the session",
    "podium_contains": "Driver finishes on the podium",
    "points_finish": "Driver finishes in the points (top 10)",
    "driver_finish_position": "Driver finishing position vs a value",
    "head_to_head_finish": "Driver A finishes ahead of Driver B",
    "classified_finish": "Driver is classified (no DNF/DNS/DSQ)",
    "driver_dnf": "Driver does not finish",
    "beats_grid": "Driver finishes ahead of their grid slot",
    "positions_gained_at_least": "Driver gains at least N positions",
    "fastest_lap_by": "Driver sets the fastest lap",
    "winning_margin": "Winning margin vs a number of seconds",
    "pit_stops": "Driver's pit-stop count vs a value",
}


@dataclass(frozen=True)
class SettlementTypeMeta:
    """A registry entry: code, human label, parameter field names, tier."""

    code: str
    label: str
    parameters: tuple[str, ...]
    tier: str = "A"


SETTLEMENT_TYPES: list[SettlementTypeMeta] = [
    SettlementTypeMeta(code, _LABELS[code], tuple(model.model_fields), "A")
    for code, (model, _fn) in GRADERS.items()
]


class SupportsUpsert(Protocol):
    def upsert(self, entity_set: str, alternate_key: str, data: Mapping[str, Any]) -> None: ...


ENTITY_SET = "racy_settlementtypes"


def seed(dataverse: SupportsUpsert) -> int:
    """Upsert the Settlement Type reference records; returns the count.

    Idempotent (upsert by ``racy_code`` alternate key). Needs the Paddock schema
    (#225) to exist for a live run; unit-tested with a fake upserter.
    """
    for meta in SETTLEMENT_TYPES:
        dataverse.upsert(
            ENTITY_SET,
            f"racy_code='{meta.code}'",
            {
                "racy_code": meta.code,
                "racy_label": meta.label,
                "racy_parameters": ",".join(meta.parameters),
                "racy_tier": meta.tier,
            },
        )
    return len(SETTLEMENT_TYPES)
