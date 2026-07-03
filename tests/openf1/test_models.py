"""Tests for OpenF1 Pydantic models and the parse_many validation helper."""

import pytest

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
    parse_many,
)


def test_session_result_valid_with_dnf_null_position() -> None:
    row = {"session_key": 9158, "driver_number": 1, "position": None, "dnf": True}
    model = SessionResult.model_validate(row)
    assert model.driver_number == 1
    assert model.position is None
    assert model.dnf is True


def test_extra_fields_ignored() -> None:
    row = {"session_key": 9158, "driver_number": 44, "position": 3, "unmapped_field": "x"}
    model = SessionResult.model_validate(row)
    assert model.position == 3
    assert not hasattr(model, "unmapped_field")


def test_optional_fields_default_none() -> None:
    driver = Driver.model_validate({"session_key": 1, "driver_number": 16})
    assert driver.full_name is None
    assert driver.team_name is None


@pytest.mark.parametrize(
    "model",
    [Session, Driver, Lap, SessionResult, StartingGrid, Pit, Position, Stint, Weather],
)
def test_missing_required_key_raises(model: type[OpenF1Record]) -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        model.model_validate({})  # missing session_key (and driver_number)


def test_type_coercion_and_error() -> None:
    # pydantic coerces a numeric string to int
    coerced = Position.model_validate({"session_key": "1", "driver_number": 2, "position": 3})
    assert coerced.session_key == 1
    # a non-numeric string is a genuine type error
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Position.model_validate({"session_key": "abc", "driver_number": 2})


# --- parse_many -------------------------------------------------------------


def test_parse_many_all_valid() -> None:
    rows = [
        {"session_key": 1, "driver_number": 1, "position": 1},
        {"session_key": 1, "driver_number": 44, "position": 2},
    ]
    result = parse_many(SessionResult, rows)
    assert result.ok
    assert len(result.valid) == 2
    assert result.errors == []


def test_parse_many_collects_failures_without_raising(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from shared.logging import configure_logging

    configure_logging(json_output=False)
    rows = [
        {"session_key": 1, "driver_number": 1, "position": 1},  # ok
        {"driver_number": 2},  # missing session_key -> error
        {"session_key": 3, "driver_number": 3},  # ok
    ]
    result = parse_many(SessionResult, rows)
    assert not result.ok
    assert len(result.valid) == 2
    assert len(result.errors) == 1
    assert result.errors[0].index == 1
    assert "failed validation" in capsys.readouterr().err


def test_parse_many_empty() -> None:
    result = parse_many(Lap, [])
    assert result.ok
    assert result.valid == []


def test_stint_and_weather_fields() -> None:
    stint = Stint.model_validate(
        {"session_key": 1, "driver_number": 1, "compound": "SOFT", "tyre_age_at_start": 2}
    )
    assert stint.compound == "SOFT"
    weather = Weather.model_validate({"session_key": 1, "rainfall": 1, "air_temperature": 24.5})
    assert weather.rainfall == 1
    assert weather.air_temperature == 24.5
