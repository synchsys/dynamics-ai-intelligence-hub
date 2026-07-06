"""Tests for the calibrated ML odds pricer (#232)."""

from paddock import HeuristicPricer, price_probability
from paddock.odds_model import ModelPricer, OddsModel, form_features, train_odds_model

# --- form features ----------------------------------------------------------


def test_form_features_from_positions() -> None:
    f = form_features([1, 3, 2, None])  # one DNF ignored
    assert f["mean_finish"] == 2.0
    assert f["win_rate"] == 1 / 3 and f["podium_rate"] == 1.0
    assert f["best_finish"] == 1.0 and f["races"] == 3.0


def test_form_features_empty_is_backmarker_prior() -> None:
    f = form_features([None, None])
    assert f["races"] == 0.0 and f["win_rate"] == 0.0 and f["mean_finish"] == 20.0


# --- shared probability -> odds --------------------------------------------


def test_price_probability_tags_source_and_applies_margin() -> None:
    fair = price_probability(0.5, source="model", house_margin=0.0)
    shortened = price_probability(0.5, source="model", house_margin=0.5)
    assert fair.source == "model"
    assert shortened.decimal_odds < fair.decimal_odds  # margin shortens the price


# --- model pricing ----------------------------------------------------------

STRONG: list[int | None] = [1, 2, 1, 3, 2]
WEAK: list[int | None] = [16, 18, 15, 17, 19]
PODIUM_ONLY: list[int | None] = [2, 1, 4, 2, 1]


def _model() -> OddsModel:
    # Strong-form drivers win/podium; weak-form drivers don't. cv=3 needs >=3/class.
    samples: list[tuple[list[int | None], bool, bool]] = []
    for _ in range(6):
        samples.append((STRONG, True, True))
        samples.append((PODIUM_ONLY, False, True))  # podium but no win
        samples.append((WEAK, False, False))
    return train_odds_model(samples, cv=3)


def _pricer() -> ModelPricer:
    form = {1: STRONG, 2: WEAK}
    return ModelPricer(_model(), form, fallback=HeuristicPricer(form))


def test_model_prices_winner_with_model_source() -> None:
    odds = _pricer().price("driver_wins", {"driver_number": 1})
    assert odds.source == "model"
    assert 0.0 < odds.probability < 1.0


def test_strong_form_priced_shorter_than_weak() -> None:
    pricer = _pricer()
    strong = pricer.price("driver_wins", {"driver_number": 1})
    weak = pricer.price("driver_wins", {"driver_number": 2})
    assert strong.probability > weak.probability  # model learned form -> win


def test_podium_uses_model() -> None:
    odds = _pricer().price("podium_contains", {"driver_number": 1})
    assert odds.source == "model" and odds.probability > 0


def test_other_types_delegate_to_fallback() -> None:
    # points_finish is not a model target -> heuristic fallback prices it.
    odds = _pricer().price("points_finish", {"driver_number": 1})
    assert odds.source == "heuristic"
