"""The data a grading function reads — a session's ingested OpenF1 rows.

Built from validated ``openf1.models`` (in-memory), so grading is a pure
function of data: no live API call at grade time (ADR-0008). The settlement
engine (#229) constructs this from Dataverse; tests build it from fixtures.
"""

from dataclasses import dataclass, field

from openf1.models import Driver, Lap, Pit, SessionResult, StartingGrid


@dataclass
class GradingContext:
    """Ingested rows for one session, with convenience lookups."""

    results: list[SessionResult] = field(default_factory=list)
    grid: list[StartingGrid] = field(default_factory=list)
    laps: list[Lap] = field(default_factory=list)
    pit: list[Pit] = field(default_factory=list)
    drivers: list[Driver] = field(default_factory=list)

    def result_for(self, driver_number: int) -> SessionResult | None:
        return next((r for r in self.results if r.driver_number == driver_number), None)

    def grid_for(self, driver_number: int) -> StartingGrid | None:
        return next((g for g in self.grid if g.driver_number == driver_number), None)

    def pit_count(self, driver_number: int) -> int:
        return sum(1 for p in self.pit if p.driver_number == driver_number)


def is_classified(result: SessionResult) -> bool:
    """A driver is classified if they finished with a position and no dnf/dns/dsq."""
    return result.position is not None and not (result.dnf or result.dns or result.dsq)
