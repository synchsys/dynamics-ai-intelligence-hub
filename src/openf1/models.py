"""Pydantic models validating OpenF1 responses before use or persistence.

Models are **lenient** (``extra="ignore"``): OpenF1 payloads carry many fields
and the API evolves, so each model captures the fields the solution actually
uses (keys, settlement-relevant columns) and ignores the rest. Only the true
keys (``session_key`` / ``driver_number`` where applicable) are required; other
fields are optional so a partial or evolving payload validates rather than
crashes.

Validation protects the Dataverse layer (story #19) and grounds the settlement
registry (#226). Use :func:`parse_many` to validate a list of raw rows and
collect per-row failures without aborting a whole ingestion run.

Field names follow the OpenF1 API; confirm against
``docs/architecture/f1-data-source-coverage.md`` and the live API when the
schema is finalised.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from shared.logging import get_logger

_logger = get_logger("openf1.models")


class OpenF1Record(BaseModel):
    """Base for OpenF1 payload models — lenient to unknown/extra fields."""

    model_config = ConfigDict(extra="ignore")


class Meeting(OpenF1Record):
    meeting_key: int
    meeting_name: str | None = None
    year: int | None = None
    country_name: str | None = None
    circuit_short_name: str | None = None
    date_start: str | None = None


class Session(OpenF1Record):
    session_key: int
    meeting_key: int | None = None
    session_name: str | None = None
    session_type: str | None = None
    date_start: str | None = None
    date_end: str | None = None
    year: int | None = None
    country_name: str | None = None


class Driver(OpenF1Record):
    session_key: int
    driver_number: int
    full_name: str | None = None
    name_acronym: str | None = None
    team_name: str | None = None


class Lap(OpenF1Record):
    session_key: int
    driver_number: int
    lap_number: int | None = None
    lap_duration: float | None = None
    is_pit_out_lap: bool | None = None
    date_start: str | None = None


class SessionResult(OpenF1Record):
    """Classification row — the settlement backbone (types 1–7, 11)."""

    session_key: int
    driver_number: int
    position: int | None = None  # null when not classified / DNF
    dnf: bool | None = None
    dns: bool | None = None
    dsq: bool | None = None
    gap_to_leader: float | None = None
    number_of_laps: int | None = None
    duration: float | None = None


class StartingGrid(OpenF1Record):
    """Grid position (types 8–9, with SessionResult)."""

    session_key: int
    driver_number: int
    position: int | None = None


class Pit(OpenF1Record):
    """Pit stop (type 12)."""

    session_key: int
    driver_number: int
    pit_duration: float | None = None
    lap_number: int | None = None


class Position(OpenF1Record):
    """Position over time (odds inputs)."""

    session_key: int
    driver_number: int
    position: int | None = None
    date: str | None = None


class Stint(OpenF1Record):
    """Tyre stint (Epic 7 strategy features)."""

    session_key: int
    driver_number: int
    stint_number: int | None = None
    compound: str | None = None
    tyre_age_at_start: int | None = None
    lap_start: int | None = None
    lap_end: int | None = None


class Weather(OpenF1Record):
    """Session weather (growth type 14)."""

    session_key: int
    air_temperature: float | None = None
    track_temperature: float | None = None
    rainfall: int | None = None
    wind_speed: float | None = None
    date: str | None = None


@dataclass
class ParseError:
    """A single row that failed validation."""

    index: int
    error: str
    row: Mapping[str, Any]


@dataclass
class ParseResult[T: OpenF1Record]:
    """Outcome of validating a batch of rows: the valid models + any failures."""

    valid: list[T] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_many[T: OpenF1Record](
    model: type[T], rows: Iterable[Mapping[str, Any]]
) -> ParseResult[T]:
    """Validate ``rows`` against ``model``, collecting failures without raising.

    A malformed row is logged and recorded in ``errors`` so a single bad record
    never aborts an ingestion run (per the story's validation contract).
    """
    result: ParseResult[T] = ParseResult()
    for index, row in enumerate(rows):
        try:
            result.valid.append(model.model_validate(row))
        except ValidationError as exc:
            _logger.warning("openf1 %s row %d failed validation: %s", model.__name__, index, exc)
            result.errors.append(ParseError(index=index, error=str(exc), row=row))
    return result
