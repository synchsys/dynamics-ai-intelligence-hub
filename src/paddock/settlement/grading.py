"""Deterministic grading functions for Settlement Types 1–12 (Tier A).

Each function reads a :class:`~paddock.settlement.context.GradingContext` and
returns an :class:`Outcome`. The rule everywhere: **VOID** when required data is
absent/ambiguous (refund, never guess); a *known* DNF grades to LOSE where a
finish was predicted. No LLM, no live API (ADR-0008).
"""

from collections.abc import Callable

from pydantic import BaseModel

from paddock.settlement.context import GradingContext, is_classified
from paddock.settlement.types import (
    DriverParams,
    DriverThresholdParams,
    HeadToHeadParams,
    Outcome,
    PitStopParams,
    PositionsGainedParams,
    WinningMarginParams,
)


def _win(cond: bool) -> Outcome:
    return Outcome.WIN if cond else Outcome.LOSE


def grade_driver_wins(p: DriverParams, ctx: GradingContext) -> Outcome:
    r = ctx.result_for(p.driver_number)
    if r is None:
        return Outcome.VOID
    return _win(r.position == 1)


def grade_podium_contains(p: DriverParams, ctx: GradingContext) -> Outcome:
    r = ctx.result_for(p.driver_number)
    if r is None:
        return Outcome.VOID
    return _win(is_classified(r) and r.position is not None and r.position <= 3)


def grade_points_finish(p: DriverParams, ctx: GradingContext) -> Outcome:
    r = ctx.result_for(p.driver_number)
    if r is None:
        return Outcome.VOID
    return _win(is_classified(r) and r.position is not None and r.position <= 10)


def grade_driver_finish_position(p: DriverThresholdParams, ctx: GradingContext) -> Outcome:
    r = ctx.result_for(p.driver_number)
    if r is None or r.position is None:
        return Outcome.VOID
    return _win(p.operator.apply(r.position, p.value))


def grade_head_to_head_finish(p: HeadToHeadParams, ctx: GradingContext) -> Outcome:
    ra, rb = ctx.result_for(p.driver_a), ctx.result_for(p.driver_b)
    if ra is None or rb is None:
        return Outcome.VOID
    a_rank = ra.position if is_classified(ra) else None
    b_rank = rb.position if is_classified(rb) else None
    if a_rank is not None and b_rank is not None:
        return _win(a_rank < b_rank)  # both classified — lower position wins
    if (a_rank is None) != (b_rank is None):
        return _win(b_rank is None)  # exactly one classified — the classified one wins
    return Outcome.VOID  # neither classified — ambiguous


def grade_classified_finish(p: DriverParams, ctx: GradingContext) -> Outcome:
    r = ctx.result_for(p.driver_number)
    if r is None:
        return Outcome.VOID
    return _win(is_classified(r))


def grade_driver_dnf(p: DriverParams, ctx: GradingContext) -> Outcome:
    r = ctx.result_for(p.driver_number)
    if r is None:
        return Outcome.VOID
    return _win(bool(r.dnf))


def grade_beats_grid(p: DriverParams, ctx: GradingContext) -> Outcome:
    r, g = ctx.result_for(p.driver_number), ctx.grid_for(p.driver_number)
    if r is None or g is None or r.position is None or g.position is None:
        return Outcome.VOID
    return _win(r.position < g.position)


def grade_positions_gained_at_least(p: PositionsGainedParams, ctx: GradingContext) -> Outcome:
    r, g = ctx.result_for(p.driver_number), ctx.grid_for(p.driver_number)
    if r is None or g is None or r.position is None or g.position is None:
        return Outcome.VOID
    return _win((g.position - r.position) >= p.n)


def grade_fastest_lap_by(p: DriverParams, ctx: GradingContext) -> Outcome:
    timed = [lap for lap in ctx.laps if lap.lap_duration is not None]
    if not timed:
        return Outcome.VOID
    fastest = min(timed, key=lambda lap: lap.lap_duration)  # type: ignore[arg-type,return-value]
    return _win(fastest.driver_number == p.driver_number)


def grade_winning_margin(p: WinningMarginParams, ctx: GradingContext) -> Outcome:
    runner_up = next((r for r in ctx.results if r.position == 2), None)
    if runner_up is None or runner_up.gap_to_leader is None:
        return Outcome.VOID
    return _win(p.operator.apply(runner_up.gap_to_leader, p.seconds))


def grade_pit_stops(p: PitStopParams, ctx: GradingContext) -> Outcome:
    if not ctx.pit:
        return Outcome.VOID
    return _win(p.operator.apply(ctx.pit_count(p.driver_number), p.n))


# code -> (param model, grading function)
GRADERS: dict[str, tuple[type[BaseModel], Callable[..., Outcome]]] = {
    "driver_wins": (DriverParams, grade_driver_wins),
    "podium_contains": (DriverParams, grade_podium_contains),
    "points_finish": (DriverParams, grade_points_finish),
    "driver_finish_position": (DriverThresholdParams, grade_driver_finish_position),
    "head_to_head_finish": (HeadToHeadParams, grade_head_to_head_finish),
    "classified_finish": (DriverParams, grade_classified_finish),
    "driver_dnf": (DriverParams, grade_driver_dnf),
    "beats_grid": (DriverParams, grade_beats_grid),
    "positions_gained_at_least": (PositionsGainedParams, grade_positions_gained_at_least),
    "fastest_lap_by": (DriverParams, grade_fastest_lap_by),
    "winning_margin": (WinningMarginParams, grade_winning_margin),
    "pit_stops": (PitStopParams, grade_pit_stops),
}


def grade(code: str, params: dict[str, object], ctx: GradingContext) -> Outcome:
    """Validate ``params`` for ``code`` and grade against ``ctx``.

    Raises ``KeyError`` for an unknown settlement type; the parameter model
    raises ``pydantic.ValidationError`` on malformed params (caught upstream).
    """
    model, func = GRADERS[code]
    return func(model.model_validate(params), ctx)
