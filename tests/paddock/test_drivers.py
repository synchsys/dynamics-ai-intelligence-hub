"""Tests for driver name -> number resolution."""

from openf1.models import Driver
from paddock.settlement import resolve_driver

DRIVERS = [
    Driver(session_key=1, driver_number=1, full_name="Max Verstappen", name_acronym="VER"),
    Driver(session_key=1, driver_number=4, full_name="Lando Norris", name_acronym="NOR"),
    Driver(session_key=1, driver_number=44, full_name="Lewis Hamilton", name_acronym="HAM"),
]


def test_int_reference_passthrough() -> None:
    assert resolve_driver(63, DRIVERS) == 63  # numbers are trusted as-is


def test_resolve_by_acronym() -> None:
    assert resolve_driver("NOR", DRIVERS) == 4
    assert resolve_driver("ham", DRIVERS) == 44  # case-insensitive


def test_resolve_by_full_name() -> None:
    assert resolve_driver("Max Verstappen", DRIVERS) == 1


def test_resolve_by_surname_token() -> None:
    assert resolve_driver("Norris", DRIVERS) == 4
    assert resolve_driver("hamilton", DRIVERS) == 44


def test_unmatched_returns_none() -> None:
    assert resolve_driver("Schumacher", DRIVERS) is None


def test_empty_returns_none() -> None:
    assert resolve_driver("   ", DRIVERS) is None


def test_ambiguous_returns_none() -> None:
    dupes = [
        Driver(session_key=1, driver_number=1, full_name="Max Verstappen", name_acronym="VER"),
        Driver(session_key=1, driver_number=2, full_name="Max Chilton", name_acronym="CHI"),
    ]
    assert resolve_driver("Max", dupes) is None  # two "Max" tokens -> ambiguous
