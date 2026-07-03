"""Tests for intake.mapping — free-text intent → validated grading parameters."""

import pytest

from openf1.models import Driver
from paddock.intake.mapping import MappingError, map_parameters
from paddock.intake.schema import WagerIntent

DRIVERS = [
    Driver(session_key=9165, driver_number=55, full_name="Carlos Sainz", name_acronym="SAI"),
    Driver(session_key=9165, driver_number=4, full_name="Lando Norris", name_acronym="NOR"),
]


def _intent(**kwargs: object) -> WagerIntent:
    return WagerIntent(decision="propose", **kwargs)


def test_driver_only_type() -> None:
    code, params = map_parameters(_intent(settlement_type="driver_wins", driver="Sainz"), DRIVERS)
    assert code == "driver_wins"
    assert params == {"driver_number": 55}


def test_head_to_head() -> None:
    _code, params = map_parameters(
        _intent(settlement_type="head_to_head_finish", driver="Sainz", driver_b="Norris"), DRIVERS
    )
    assert params == {"driver_a": 55, "driver_b": 4}


def test_finish_position_threshold() -> None:
    _code, params = map_parameters(
        _intent(settlement_type="driver_finish_position", driver="Norris", operator="<=", number=2),
        DRIVERS,
    )
    assert params == {"driver_number": 4, "operator": "<=", "value": 2}


def test_positions_gained() -> None:
    _code, params = map_parameters(
        _intent(settlement_type="positions_gained_at_least", driver="Sainz", number=3), DRIVERS
    )
    assert params == {"driver_number": 55, "n": 3}


def test_pit_stops() -> None:
    _code, params = map_parameters(
        _intent(settlement_type="pit_stops", driver="Sainz", operator="<=", number=2), DRIVERS
    )
    assert params == {"driver_number": 55, "operator": "<=", "n": 2}


def test_winning_margin_has_no_driver() -> None:
    _code, params = map_parameters(
        _intent(settlement_type="winning_margin", operator="<", number=1.0), DRIVERS
    )
    assert params == {"operator": "<", "seconds": 1.0}


def test_unknown_type_rejected() -> None:
    with pytest.raises(MappingError, match="not a prediction type"):
        map_parameters(_intent(settlement_type="who_knows", driver="Sainz"), DRIVERS)


def test_unresolved_driver_rejected() -> None:
    with pytest.raises(MappingError, match="couldn't identify the driver"):
        map_parameters(_intent(settlement_type="driver_wins", driver="Nobody"), DRIVERS)


def test_missing_driver_rejected() -> None:
    with pytest.raises(MappingError, match="name the driver"):
        map_parameters(_intent(settlement_type="driver_wins"), DRIVERS)


def test_missing_operator_rejected() -> None:
    with pytest.raises(MappingError, match="comparison"):
        map_parameters(
            _intent(settlement_type="driver_finish_position", driver="Norris", number=2), DRIVERS
        )


def test_missing_number_rejected() -> None:
    with pytest.raises(MappingError, match="needs a number"):
        map_parameters(
            _intent(settlement_type="positions_gained_at_least", driver="Sainz"), DRIVERS
        )


def test_winning_margin_missing_number_rejected() -> None:
    with pytest.raises(MappingError, match="seconds"):
        map_parameters(_intent(settlement_type="winning_margin", operator="<"), DRIVERS)


def test_head_to_head_missing_second_driver_rejected() -> None:
    with pytest.raises(MappingError, match="name the driver"):
        map_parameters(_intent(settlement_type="head_to_head_finish", driver="Sainz"), DRIVERS)


def test_schema_invalid_params_rejected() -> None:
    # Defensive branch: bypass WagerIntent validation to feed an invalid operator
    # through to the param model, which must reject it as a guided MappingError.
    bad = WagerIntent.model_construct(
        decision="propose",
        settlement_type="driver_finish_position",
        driver="Norris",
        operator="INVALID",  # type: ignore[arg-type]
        number=2,
    )
    with pytest.raises(MappingError, match="couldn't build valid parameters"):
        map_parameters(bad, DRIVERS)
