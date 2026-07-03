"""Tests for the v1 recent-form heuristic odds pricer."""

import pytest

from paddock.odds import HeuristicPricer, Odds
from paddock.settlement.grading import GRADERS

# driver 1 = form favourite, driver 2 = mid, driver 3 = backmarker.
FORM: dict[int, list[int | None]] = {
    1: [1, 1, 2, 1, 3],
    2: [6, 8, 5, 7, 6],
    3: [15, 18, 12, 20, None],  # None = DNF
}

# Minimal valid params per settlement type (for the "every type prices" sweep).
PARAMS: dict[str, dict[str, object]] = {
    "driver_wins": {"driver_number": 1},
    "podium_contains": {"driver_number": 1},
    "points_finish": {"driver_number": 1},
    "driver_finish_position": {"driver_number": 1, "operator": "<=", "value": 5},
    "head_to_head_finish": {"driver_a": 1, "driver_b": 3},
    "classified_finish": {"driver_number": 1},
    "driver_dnf": {"driver_number": 3},
    "beats_grid": {"driver_number": 1},
    "positions_gained_at_least": {"driver_number": 1, "n": 3},
    "fastest_lap_by": {"driver_number": 1},
    "winning_margin": {"operator": "<=", "seconds": 5.0},
    "pit_stops": {"driver_number": 1, "operator": ">=", "n": 2},
}


def pricer(margin: float = 0.10) -> HeuristicPricer:
    return HeuristicPricer(FORM, house_margin=margin)


def test_every_tier_a_type_returns_valid_odds() -> None:
    p = pricer()
    assert set(PARAMS) == set(GRADERS)  # coverage of all 12 types
    for code, params in PARAMS.items():
        odds = p.price(code, params)
        assert isinstance(odds, Odds)
        assert odds.source == "heuristic"
        assert 0.0 < odds.probability < 1.0
        assert odds.decimal_odds > 1.0, code


def test_favourite_prices_shorter_than_backmarker() -> None:
    p = pricer()
    fav = p.price("driver_wins", {"driver_number": 1})
    back = p.price("driver_wins", {"driver_number": 3})
    assert fav.probability > back.probability
    assert fav.decimal_odds < back.decimal_odds


def test_podium_favourite_shorter() -> None:
    p = pricer()
    assert (
        p.price("podium_contains", {"driver_number": 1}).decimal_odds
        < p.price("podium_contains", {"driver_number": 3}).decimal_odds
    )


def test_house_margin_shortens_odds() -> None:
    low = pricer(0.05).price("beats_grid", {"driver_number": 1})  # fixed 0.5 prior
    high = pricer(0.50).price("beats_grid", {"driver_number": 1})
    assert low.probability == high.probability
    assert high.decimal_odds < low.decimal_odds  # bigger margin -> shorter price
    assert high.decimal_odds > 1.0


def test_finish_position_operator_directions() -> None:
    p = pricer()
    easy = p.price("driver_finish_position", {"driver_number": 1, "operator": "<=", "value": 10})
    hard = p.price("driver_finish_position", {"driver_number": 1, "operator": ">=", "value": 15})
    assert easy.probability > hard.probability


@pytest.mark.parametrize("op", ["<=", "<", ">=", ">", "==", "!="])
def test_finish_position_all_operators_price(op: str) -> None:
    odds = pricer().price(
        "driver_finish_position", {"driver_number": 1, "operator": op, "value": 5}
    )
    assert 0.0 < odds.probability < 1.0
    assert odds.decimal_odds > 1.0


def test_winning_margin_direction() -> None:
    p = pricer()
    within = p.price("winning_margin", {"operator": "<=", "seconds": 8.0})
    over = p.price("winning_margin", {"operator": ">=", "seconds": 8.0})
    assert abs(within.probability + over.probability - 1.0) < 1e-9


def test_head_to_head_orders_by_form() -> None:
    p = pricer()
    strong = p.price("head_to_head_finish", {"driver_a": 1, "driver_b": 3})  # fav vs backmarker
    weak = p.price("head_to_head_finish", {"driver_a": 3, "driver_b": 1})
    assert strong.probability > 0.5
    assert strong.decimal_odds < weak.decimal_odds


def test_empty_form_falls_back_without_crashing() -> None:
    p = HeuristicPricer({}, house_margin=0.1)
    odds = p.price("driver_wins", {"driver_number": 99})
    assert 0.0 < odds.probability < 1.0
    # head-to-head with no data -> even
    assert p.price("head_to_head_finish", {"driver_a": 1, "driver_b": 2}).probability == 0.5


def test_unknown_type_raises() -> None:
    with pytest.raises(KeyError):
        pricer().price("no_such_type", {})
