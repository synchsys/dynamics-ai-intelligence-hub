"""Win/lose/void tests for every Tier-A grading function (types 1–12)."""

import pytest

from openf1.models import Lap, Pit, SessionResult, StartingGrid
from paddock.settlement import GradingContext, Operator, Outcome, grade
from paddock.settlement.grading import (
    grade_beats_grid,
    grade_classified_finish,
    grade_driver_dnf,
    grade_driver_finish_position,
    grade_driver_wins,
    grade_fastest_lap_by,
    grade_head_to_head_finish,
    grade_pit_stops,
    grade_podium_contains,
    grade_points_finish,
    grade_positions_gained_at_least,
    grade_winning_margin,
)
from paddock.settlement.types import (
    DriverParams,
    DriverThresholdParams,
    HeadToHeadParams,
    PitStopParams,
    PositionsGainedParams,
    WinningMarginParams,
)


def sr(
    dn: int,
    position: int | None = None,
    *,
    dnf: bool = False,
    dns: bool = False,
    dsq: bool = False,
    gap: float | None = None,
) -> SessionResult:
    return SessionResult(
        session_key=1,
        driver_number=dn,
        position=position,
        dnf=dnf,
        dns=dns,
        dsq=dsq,
        gap_to_leader=gap,
    )


def sg(dn: int, position: int) -> StartingGrid:
    return StartingGrid(session_key=1, driver_number=dn, position=position)


def lp(dn: int, dur: float, n: int = 1) -> Lap:
    return Lap(session_key=1, driver_number=dn, lap_number=n, lap_duration=dur)


def pt(dn: int, n: int) -> Pit:
    return Pit(session_key=1, driver_number=dn, lap_number=n)


D = DriverParams(driver_number=1)


# 1. driver_wins
def test_driver_wins_win() -> None:
    assert grade_driver_wins(D, GradingContext(results=[sr(1, 1)])) is Outcome.WIN


def test_driver_wins_lose() -> None:
    assert grade_driver_wins(D, GradingContext(results=[sr(1, 2)])) is Outcome.LOSE


def test_driver_wins_void() -> None:
    assert grade_driver_wins(D, GradingContext(results=[sr(2, 1)])) is Outcome.VOID


# 2. podium_contains
def test_podium_win() -> None:
    assert grade_podium_contains(D, GradingContext(results=[sr(1, 3)])) is Outcome.WIN


def test_podium_lose_dnf() -> None:
    assert grade_podium_contains(D, GradingContext(results=[sr(1, None, dnf=True)])) is Outcome.LOSE


def test_podium_void() -> None:
    assert grade_podium_contains(D, GradingContext(results=[])) is Outcome.VOID


# 3. points_finish
def test_points_win() -> None:
    assert grade_points_finish(D, GradingContext(results=[sr(1, 10)])) is Outcome.WIN


def test_points_lose() -> None:
    assert grade_points_finish(D, GradingContext(results=[sr(1, 11)])) is Outcome.LOSE


def test_points_void() -> None:
    assert grade_points_finish(D, GradingContext(results=[])) is Outcome.VOID


# 4. driver_finish_position
def test_finish_position_win() -> None:
    p = DriverThresholdParams(driver_number=1, operator=Operator.LE, value=5)
    assert grade_driver_finish_position(p, GradingContext(results=[sr(1, 3)])) is Outcome.WIN


def test_finish_position_lose() -> None:
    p = DriverThresholdParams(driver_number=1, operator=Operator.LE, value=5)
    assert grade_driver_finish_position(p, GradingContext(results=[sr(1, 8)])) is Outcome.LOSE


def test_finish_position_void_null() -> None:
    p = DriverThresholdParams(driver_number=1, operator=Operator.LE, value=5)
    assert (
        grade_driver_finish_position(p, GradingContext(results=[sr(1, None, dnf=True)]))
        is Outcome.VOID
    )


# 5. head_to_head_finish
def test_h2h_win() -> None:
    p = HeadToHeadParams(driver_a=1, driver_b=2)
    assert grade_head_to_head_finish(p, GradingContext(results=[sr(1, 1), sr(2, 2)])) is Outcome.WIN


def test_h2h_lose_one_classified() -> None:
    p = HeadToHeadParams(driver_a=1, driver_b=2)
    ctx = GradingContext(results=[sr(1, None, dnf=True), sr(2, 4)])
    assert grade_head_to_head_finish(p, ctx) is Outcome.LOSE


def test_h2h_lose_both_classified() -> None:
    p = HeadToHeadParams(driver_a=1, driver_b=2)
    ctx = GradingContext(results=[sr(1, 5), sr(2, 2)])  # A behind B
    assert grade_head_to_head_finish(p, ctx) is Outcome.LOSE


def test_h2h_win_one_classified() -> None:
    p = HeadToHeadParams(driver_a=1, driver_b=2)
    ctx = GradingContext(results=[sr(1, 4), sr(2, None, dnf=True)])  # A classified, B DNF
    assert grade_head_to_head_finish(p, ctx) is Outcome.WIN


def test_h2h_void_both_dnf() -> None:
    p = HeadToHeadParams(driver_a=1, driver_b=2)
    ctx = GradingContext(results=[sr(1, None, dnf=True), sr(2, None, dnf=True)])
    assert grade_head_to_head_finish(p, ctx) is Outcome.VOID


def test_h2h_void_missing_result() -> None:
    p = HeadToHeadParams(driver_a=1, driver_b=2)
    ctx = GradingContext(results=[sr(1, 1)])  # no result row for driver 2
    assert grade_head_to_head_finish(p, ctx) is Outcome.VOID


# 6. classified_finish
def test_classified_win() -> None:
    assert grade_classified_finish(D, GradingContext(results=[sr(1, 12)])) is Outcome.WIN


def test_classified_lose() -> None:
    assert (
        grade_classified_finish(D, GradingContext(results=[sr(1, None, dnf=True)])) is Outcome.LOSE
    )


def test_classified_void() -> None:
    assert grade_classified_finish(D, GradingContext(results=[])) is Outcome.VOID


# 7. driver_dnf
def test_dnf_win() -> None:
    assert grade_driver_dnf(D, GradingContext(results=[sr(1, None, dnf=True)])) is Outcome.WIN


def test_dnf_lose() -> None:
    assert grade_driver_dnf(D, GradingContext(results=[sr(1, 5)])) is Outcome.LOSE


def test_dnf_void() -> None:
    assert grade_driver_dnf(D, GradingContext(results=[])) is Outcome.VOID


# 8. beats_grid
def test_beats_grid_win() -> None:
    ctx = GradingContext(results=[sr(1, 1)], grid=[sg(1, 5)])
    assert grade_beats_grid(D, ctx) is Outcome.WIN


def test_beats_grid_lose() -> None:
    ctx = GradingContext(results=[sr(1, 6)], grid=[sg(1, 3)])
    assert grade_beats_grid(D, ctx) is Outcome.LOSE


def test_beats_grid_void_no_grid() -> None:
    assert grade_beats_grid(D, GradingContext(results=[sr(1, 1)])) is Outcome.VOID


# 9. positions_gained_at_least
def test_positions_gained_win() -> None:
    p = PositionsGainedParams(driver_number=1, n=5)
    ctx = GradingContext(results=[sr(1, 3)], grid=[sg(1, 10)])
    assert grade_positions_gained_at_least(p, ctx) is Outcome.WIN


def test_positions_gained_lose() -> None:
    p = PositionsGainedParams(driver_number=1, n=5)
    ctx = GradingContext(results=[sr(1, 2)], grid=[sg(1, 3)])
    assert grade_positions_gained_at_least(p, ctx) is Outcome.LOSE


def test_positions_gained_void() -> None:
    p = PositionsGainedParams(driver_number=1, n=5)
    assert grade_positions_gained_at_least(p, GradingContext(results=[sr(1, 2)])) is Outcome.VOID


# 10. fastest_lap_by
def test_fastest_lap_win() -> None:
    ctx = GradingContext(laps=[lp(1, 80.5), lp(2, 81.2)])
    assert grade_fastest_lap_by(D, ctx) is Outcome.WIN


def test_fastest_lap_lose() -> None:
    ctx = GradingContext(laps=[lp(1, 82.0), lp(2, 80.1)])
    assert grade_fastest_lap_by(D, ctx) is Outcome.LOSE


def test_fastest_lap_void_no_laps() -> None:
    assert grade_fastest_lap_by(D, GradingContext(laps=[])) is Outcome.VOID


# 11. winning_margin
def test_winning_margin_win() -> None:
    p = WinningMarginParams(operator=Operator.LE, seconds=5.0)
    ctx = GradingContext(results=[sr(1, 1), sr(2, 2, gap=2.3)])
    assert grade_winning_margin(p, ctx) is Outcome.WIN


def test_winning_margin_lose() -> None:
    p = WinningMarginParams(operator=Operator.LE, seconds=5.0)
    ctx = GradingContext(results=[sr(1, 1), sr(2, 2, gap=10.0)])
    assert grade_winning_margin(p, ctx) is Outcome.LOSE


def test_winning_margin_void_no_p2() -> None:
    p = WinningMarginParams(operator=Operator.LE, seconds=5.0)
    assert grade_winning_margin(p, GradingContext(results=[sr(1, 1)])) is Outcome.VOID


# 12. pit_stops
def test_pit_stops_win() -> None:
    p = PitStopParams(driver_number=1, operator=Operator.GE, n=2)
    ctx = GradingContext(pit=[pt(1, 12), pt(1, 30)])
    assert grade_pit_stops(p, ctx) is Outcome.WIN


def test_pit_stops_lose() -> None:
    p = PitStopParams(driver_number=1, operator=Operator.GE, n=2)
    ctx = GradingContext(pit=[pt(1, 12), pt(2, 15)])
    assert grade_pit_stops(p, ctx) is Outcome.LOSE


def test_pit_stops_void_no_pit_data() -> None:
    p = PitStopParams(driver_number=1, operator=Operator.GE, n=2)
    assert grade_pit_stops(p, GradingContext(pit=[])) is Outcome.VOID


# --- dispatcher + operator -------------------------------------------------


def test_grade_dispatcher_validates_and_grades() -> None:
    ctx = GradingContext(results=[sr(1, 1)])
    assert grade("driver_wins", {"driver_number": 1}, ctx) is Outcome.WIN


def test_grade_dispatcher_unknown_code() -> None:
    with pytest.raises(KeyError):
        grade("no_such_type", {}, GradingContext())


def test_grade_dispatcher_bad_params() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        grade(
            "driver_finish_position", {"driver_number": 1}, GradingContext()
        )  # missing operator/value


def test_operator_apply() -> None:
    assert Operator.LE.apply(3, 5) is True
    assert Operator.GT.apply(3, 5) is False
    assert Operator.EQ.apply(2, 2) is True
