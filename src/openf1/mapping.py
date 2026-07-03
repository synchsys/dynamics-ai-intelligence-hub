"""OpenF1 → Dataverse table/field mapping (the single place to finalise names).

Each :class:`EntityMap` binds an OpenF1 payload (validated by ``openf1.models``)
to a Dataverse entity set, its alternate-key columns (for idempotent upsert),
and the OpenF1-field → Dataverse-column map. Logical names use the **`racy_`**
publisher prefix.

These names are **provisional** until the Dataverse schema (Epic 3, story #6)
is created in the environment — this module is where they get confirmed. See
``docs/architecture/openf1-mapping.md``.
"""

from dataclasses import dataclass

from openf1.models import (
    Driver,
    Lap,
    OpenF1Record,
    Pit,
    Position,
    Session,
    SessionResult,
    StartingGrid,
    Stint,
    Weather,
)

PREFIX = "racy_"


@dataclass(frozen=True)
class EntityMap:
    """Binds an OpenF1 endpoint/model to a Dataverse entity set + field mapping."""

    endpoint: str  # OpenF1Client method suffix, e.g. "session_result" -> get_session_result
    client_method: str
    model: type[OpenF1Record]
    entity_set: str  # Dataverse entity set (plural logical name)
    alt_key_fields: tuple[str, ...]  # OpenF1 field names forming the alternate key
    field_map: dict[str, str]  # OpenF1 field -> Dataverse column logical name


def _f(name: str) -> str:
    return f"{PREFIX}{name}"


# Session-scoped endpoints ingested for settlement + analytics. Composite
# alternate key is (session_key, driver_number) except where noted.
MAPPINGS: dict[str, EntityMap] = {
    "sessions": EntityMap(
        "sessions",
        "get_sessions",
        Session,
        f"{PREFIX}sessions",
        ("session_key",),
        {
            "session_key": _f("sessionkey"),
            "meeting_key": _f("meetingkey"),
            "session_name": _f("sessionname"),
            "session_type": _f("sessiontype"),
            "date_start": _f("datestart"),
            "date_end": _f("dateend"),
            "year": _f("year"),
        },
    ),
    "drivers": EntityMap(
        "drivers",
        "get_drivers",
        Driver,
        f"{PREFIX}drivers",
        ("session_key", "driver_number"),
        {
            "session_key": _f("sessionkey"),
            "driver_number": _f("drivernumber"),
            "full_name": _f("fullname"),
            "name_acronym": _f("acronym"),
            "team_name": _f("teamname"),
        },
    ),
    "session_result": EntityMap(
        "session_result",
        "get_session_result",
        SessionResult,
        f"{PREFIX}sessionresults",
        ("session_key", "driver_number"),
        {
            "session_key": _f("sessionkey"),
            "driver_number": _f("drivernumber"),
            "position": _f("position"),
            "dnf": _f("dnf"),
            "dns": _f("dns"),
            "dsq": _f("dsq"),
            "gap_to_leader": _f("gaptoleader"),
            "number_of_laps": _f("numberoflaps"),
        },
    ),
    "starting_grid": EntityMap(
        "starting_grid",
        "get_starting_grid",
        StartingGrid,
        f"{PREFIX}startinggrids",
        ("session_key", "driver_number"),
        {
            "session_key": _f("sessionkey"),
            "driver_number": _f("drivernumber"),
            "position": _f("gridposition"),
        },
    ),
    "laps": EntityMap(
        "laps",
        "get_laps",
        Lap,
        f"{PREFIX}laps",
        ("session_key", "driver_number", "lap_number"),
        {
            "session_key": _f("sessionkey"),
            "driver_number": _f("drivernumber"),
            "lap_number": _f("lapnumber"),
            "lap_duration": _f("lapduration"),
        },
    ),
    "pit": EntityMap(
        "pit",
        "get_pit",
        Pit,
        f"{PREFIX}pitstops",
        ("session_key", "driver_number", "lap_number"),
        {
            "session_key": _f("sessionkey"),
            "driver_number": _f("drivernumber"),
            "lap_number": _f("lapnumber"),
            "pit_duration": _f("pitduration"),
        },
    ),
    "position": EntityMap(
        "position",
        "get_position",
        Position,
        f"{PREFIX}positions",
        ("session_key", "driver_number", "date"),
        {
            "session_key": _f("sessionkey"),
            "driver_number": _f("drivernumber"),
            "position": _f("position"),
            "date": _f("recordedon"),
        },
    ),
    "stints": EntityMap(
        "stints",
        "get_stints",
        Stint,
        f"{PREFIX}stints",
        ("session_key", "driver_number", "stint_number"),
        {
            "session_key": _f("sessionkey"),
            "driver_number": _f("drivernumber"),
            "stint_number": _f("stintnumber"),
            "compound": _f("compound"),
            "tyre_age_at_start": _f("tyreage"),
        },
    ),
    "weather": EntityMap(
        "weather",
        "get_weather",
        Weather,
        f"{PREFIX}weather",
        ("session_key", "date"),
        {
            "session_key": _f("sessionkey"),
            "air_temperature": _f("airtemp"),
            "track_temperature": _f("tracktemp"),
            "rainfall": _f("rainfall"),
            "date": _f("recordedon"),
        },
    ),
}

# Endpoints whose presence makes a race event settleable (Tier-A minimum).
SETTLEMENT_REQUIRED = ("drivers", "session_result")
