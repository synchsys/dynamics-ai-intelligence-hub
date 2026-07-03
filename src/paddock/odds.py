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


@dataclass(frozen=True)
class Odds:
    """A price: the fair probability, the offered decimal odds, and its source."""

    probability: float
    decimal_odds: float
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
        return Odds(probability=prob, decimal_odds=round(max(offered, 1.01), 2), source="heuristic")

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
