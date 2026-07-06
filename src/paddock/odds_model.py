"""Calibrated ML odds pricing — v2 (#232, Epic 7).

A calibrated winner/podium probability model that implements the same
:class:`~paddock.odds.OddsPricer` interface as the heuristic (12.PA-6) and tags
its odds ``source = "model"``, completing the heuristic → model narrative. It
prices ``driver_wins`` and ``podium_contains`` from a driver's recent-form
features via a calibrated classifier, and delegates the other settlement types to
a fallback pricer (the heuristic), so it fully satisfies the pricing contract.

Requires the ``analytics`` extra (scikit-learn). Probability → odds conversion is
shared with the heuristic via ``paddock.odds.price_probability``.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression

from paddock.odds import FormTable, Odds, OddsPricer, price_probability

FEATURE_ORDER = ("mean_finish", "win_rate", "podium_rate", "best_finish", "races")
_NO_FORM = 20.0  # a back-of-grid prior when a driver has no history


def form_features(positions: Sequence[int | None]) -> dict[str, float]:
    """Recent-form features from a driver's finishing positions (None = DNF/unclassified)."""
    finished = [p for p in positions if p is not None]
    n = len(finished)
    if n == 0:
        return {
            "mean_finish": _NO_FORM,
            "win_rate": 0.0,
            "podium_rate": 0.0,
            "best_finish": _NO_FORM,
            "races": 0.0,
        }
    return {
        "mean_finish": sum(finished) / n,
        "win_rate": sum(1 for p in finished if p == 1) / n,
        "podium_rate": sum(1 for p in finished if p <= 3) / n,
        "best_finish": float(min(finished)),
        "races": float(n),
    }


def _row(features: Mapping[str, float]) -> list[float]:
    return [features[name] for name in FEATURE_ORDER]


@dataclass(frozen=True)
class OddsModel:
    """Calibrated win + podium probability models."""

    win_model: Any
    podium_model: Any


def train_odds_model(
    samples: Sequence[tuple[Sequence[int | None], bool, bool]], *, cv: int = 3
) -> OddsModel:
    """Fit calibrated win/podium models from ``(form_positions, won, podium)`` samples."""
    features = [_row(form_features(positions)) for positions, _won, _pod in samples]
    won = [w for _pos, w, _pod in samples]
    podium = [p for _pos, _w, p in samples]

    def _fit(target: list[bool]) -> CalibratedClassifierCV:
        base = LogisticRegression(max_iter=1000)
        return CalibratedClassifierCV(base, cv=cv, method="sigmoid").fit(features, target)

    return OddsModel(win_model=_fit(won), podium_model=_fit(podium))


class ModelPricer:
    """Prices winner/podium via the calibrated model; delegates the rest to a fallback."""

    def __init__(
        self,
        model: OddsModel,
        form: FormTable,
        *,
        fallback: OddsPricer,
        house_margin: float = 0.10,
    ) -> None:
        self._model = model
        self._form = form
        self._fallback = fallback
        self._margin = house_margin

    def _probability(self, classifier: Any, driver_number: int) -> float:
        features = form_features(self._form.get(driver_number, []))
        return float(classifier.predict_proba([_row(features)])[0][1])

    def price(self, settlement_type: str, parameters: Mapping[str, Any]) -> Odds:
        if settlement_type == "driver_wins":
            prob = self._probability(self._model.win_model, int(parameters["driver_number"]))
            return price_probability(prob, source="model", house_margin=self._margin)
        if settlement_type == "podium_contains":
            prob = self._probability(self._model.podium_model, int(parameters["driver_number"]))
            return price_probability(prob, source="model", house_margin=self._margin)
        return self._fallback.price(settlement_type, parameters)
