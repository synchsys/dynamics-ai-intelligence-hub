"""Odds pricing — v1 recent-form heuristic behind a stable pricer interface.

The :class:`OddsPricer` protocol is the **contract**: ``price(settlement_type,
parameters) -> Odds``. This module ships :class:`HeuristicPricer` (``source =
"heuristic"``); the Epic 7 model (story #232) later implements the same protocol
with ``source = "model"`` — same odds field, different provenance.

Form-based types (win/podium/points/finish-position/classified/dnf/head-to-head)
are priced from recent ingested finishing positions with Laplace smoothing, so a
form favourite prices shorter than a backmarker. The structural types
(beats_grid, positions_gained, fastest_lap, winning_margin, pit_stops) use simple
documented priors so **every Tier-A type returns odds** — these are exactly the
ones the ML model is expected to improve.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from paddock.settlement.types import Operator

# driver_number -> recent finishing positions, most-recent first; None = DNF/unclassified.
FormTable = Mapping[int, Sequence[int | None]]

_ALPHA = 0.5  # Laplace smoothing; keeps probabilities in the open interval (0, 1)
_MIN_PROB = 0.01
_MAX_PROB = 0.99

# The traditional UK bookmaker fractional ladder (num, den), in the display forms
# bookmakers actually use (6/4, 11/8, 9/4, ...), ascending by value. Odds are
# quoted by snapping to the nearest rung, so a punter sees real prices like
# "2/1 against" or "1/2 on" — never "2.73". The shortest/longest rungs also floor
# and cap the price at realistic values.
_LADDER: tuple[tuple[int, int], ...] = (
    (1, 10),
    (1, 8),
    (1, 6),
    (1, 5),
    (1, 4),
    (2, 7),
    (3, 10),
    (1, 3),
    (2, 5),
    (4, 9),
    (1, 2),
    (8, 15),
    (4, 7),
    (8, 11),
    (4, 5),
    (5, 6),
    (10, 11),  # odds-on
    (1, 1),  # evens
    (11, 10),
    (6, 5),
    (5, 4),
    (11, 8),
    (6, 4),
    (13, 8),
    (7, 4),
    (15, 8),
    (2, 1),  # against
    (9, 4),
    (5, 2),
    (11, 4),
    (3, 1),
    (7, 2),
    (4, 1),
    (9, 2),
    (5, 1),
    (6, 1),
    (7, 1),
    (8, 1),
    (10, 1),
    (12, 1),
    (14, 1),
    (16, 1),
    (20, 1),
    (25, 1),
    (33, 1),
    (40, 1),
    (50, 1),
    (66, 1),
    (80, 1),
    (100, 1),
    (150, 1),
    (200, 1),
)


def decimal_to_fraction(decimal_odds: float) -> tuple[int, int]:
    """Snap a decimal price to the nearest standard fractional-odds rung."""
    target_profit = decimal_odds - 1.0  # fractional value = decimal - 1
    return min(_LADDER, key=lambda nd: abs(nd[0] / nd[1] - target_profit))


def fractional_line(num: int, den: int) -> str:
    """Human betting line for a fraction: '2/1 against', '1/2 on', or 'evens'."""
    if num == den:
        return "evens"
    kind = "against" if num > den else "on"
    return f"{num}/{den} {kind}"


@dataclass(frozen=True)
class Odds:
    """A price expressed the way a punter reads it.

    ``decimal_odds`` is the total-return multiplier (``= fractional + 1``) used
    for settlement payout; ``fractional`` (e.g. ``"2/1"``) and ``line``
    (e.g. ``"2/1 against"``) are the real-world display, snapped to the
    bookmaker ladder. ``probability`` is the fair estimate before margin.
    """

    probability: float
    decimal_odds: float
    fractional: str
    line: str
    source: str


def _clamp(prob: float) -> float:
    return max(_MIN_PROB, min(_MAX_PROB, prob))


def _finished(positions: Sequence[int | None]) -> list[int]:
    return [p for p in positions if p is not None]


def _p_at_most(positions: Sequence[int | None], k: int) -> float:
    """Smoothed empirical P(classified finish <= k) over recent form."""
    n = len(positions)
    hits = sum(1 for p in positions if p is not None and p <= k)
    return _clamp((hits + _ALPHA) / (n + 2 * _ALPHA)) if n else 0.5


def _p_classified(positions: Sequence[int | None]) -> float:
    n = len(positions)
    hits = sum(1 for p in positions if p is not None)
    return _clamp((hits + _ALPHA) / (n + 2 * _ALPHA)) if n else 0.5


def _mean_finish(positions: Sequence[int | None]) -> float | None:
    classified = _finished(positions)
    return sum(classified) / len(classified) if classified else None


def _threshold_prob(positions: Sequence[int | None], op: Operator, value: int) -> float:
    """P(operator(finish_position, value)) from recent form."""
    if op is Operator.LE:
        return _p_at_most(positions, value)
    if op is Operator.LT:
        return _p_at_most(positions, value - 1)
    if op is Operator.GE:
        return _clamp(1.0 - _p_at_most(positions, value - 1))
    if op is Operator.GT:
        return _clamp(1.0 - _p_at_most(positions, value))
    # EQ / NE — coarse: exact finishing position is rare
    n = len(positions) or 1
    exact = _clamp((sum(1 for p in positions if p == value) + _ALPHA) / (n + 2 * _ALPHA))
    return exact if op is Operator.EQ else _clamp(1.0 - exact)


class OddsPricer(Protocol):
    """The pricing contract shared by the heuristic (v1) and ML model (v2)."""

    def price(self, settlement_type: str, parameters: Mapping[str, Any]) -> Odds: ...


class HeuristicPricer:
    """Recent-form heuristic pricer (``source = "heuristic"``)."""

    def __init__(self, form: FormTable, *, house_margin: float = 0.10) -> None:
        self._form = form
        self._margin = house_margin

    def _positions(self, driver_number: int) -> Sequence[int | None]:
        return self._form.get(driver_number, [])

    def _odds(self, probability: float) -> Odds:
        prob = _clamp(probability)
        offered = (1.0 / prob) / (1.0 + self._margin)  # house margin shortens the price
        num, den = decimal_to_fraction(offered)  # quote a real bookmaker fraction
        decimal_odds = round(num / den + 1.0, 2)  # consistent with the quoted fraction
        return Odds(
            probability=prob,
            decimal_odds=decimal_odds,
            fractional=f"{num}/{den}",
            line=fractional_line(num, den),
            source="heuristic",
        )

    def _probability(self, settlement_type: str, params: Mapping[str, Any]) -> float:
        dn = int(params.get("driver_number", 0))
        pos = self._positions(dn)
        match settlement_type:
            case "driver_wins":
                return _p_at_most(pos, 1)
            case "podium_contains":
                return _p_at_most(pos, 3)
            case "points_finish":
                return _p_at_most(pos, 10)
            case "driver_finish_position":
                return _threshold_prob(pos, Operator(params["operator"]), int(params["value"]))
            case "classified_finish":
                return _p_classified(pos)
            case "driver_dnf":
                return _clamp(1.0 - _p_classified(pos))
            case "head_to_head_finish":
                ma = _mean_finish(self._positions(int(params["driver_a"])))
                mb = _mean_finish(self._positions(int(params["driver_b"])))
                if ma is None or mb is None:
                    return 0.5
                return _clamp(mb / (ma + mb))  # lower mean finish -> higher prob A wins
            # --- structural types: documented v1 priors (improved by the ML model) ---
            case "beats_grid":
                return 0.5  # no grid history in v1
            case "positions_gained_at_least":
                return _clamp(0.5 - 0.08 * int(params.get("n", 1)))
            case "fastest_lap_by":
                return _clamp(0.5 * _p_at_most(pos, 3))  # roughly tracks front-runners
            case "winning_margin":
                seconds = float(params.get("seconds", 0.0))
                base = _clamp(seconds / 20.0)  # larger threshold -> more likely "within"
                op = Operator(params["operator"])
                return base if op in (Operator.LE, Operator.LT) else _clamp(1.0 - base)
            case "pit_stops":
                return 0.4  # typical count prior
            case _:
                raise KeyError(f"unknown settlement type: {settlement_type}")

    def price(self, settlement_type: str, parameters: Mapping[str, Any]) -> Odds:
        return self._odds(self._probability(settlement_type, parameters))
