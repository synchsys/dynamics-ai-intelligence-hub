"""Lap-time regression — the core supervised workflow (#49).

Predicts lap time from the lap/stint features (#51) with a gradient-boosting
regressor, compared against a naive (train-mean) baseline on a **leakage-free,
grouped** hold-out. Splits are grouped by driver so no driver appears in both
train and test — the model must generalise, not memorise a driver's pace. Metrics
(MAE/RMSE/R²) and a run record are returned for logging (#56 formalises tracking).

Deterministic given ``random_state``; pure sklearn/pandas so it is unit-testable
on synthetic data without network. ``scripts/ml/train_lap_regression.py`` runs it
on a live FastF1 session.
"""

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit

from fastf1_analytics.analysis import clean_laps
from ml.features import lap_features
from shared.logging import get_logger

_logger = get_logger("ml.regression")


@dataclass(frozen=True)
class RegressionMetrics:
    """Held-out regression metrics (seconds for MAE/RMSE)."""

    mae: float
    rmse: float
    r2: float


def evaluate(y_true: Any, y_pred: Any) -> RegressionMetrics:
    return RegressionMetrics(
        mae=round(float(mean_absolute_error(y_true, y_pred)), 4),
        rmse=round(float(mean_squared_error(y_true, y_pred)) ** 0.5, 4),
        r2=round(float(r2_score(y_true, y_pred)), 4),
    )


@dataclass(frozen=True)
class LapRegressionResult:
    """Outcome of a lap-time regression run."""

    baseline: RegressionMetrics
    model: RegressionMetrics
    n_train: int
    n_test: int
    features: list[str]

    @property
    def beats_baseline(self) -> bool:
        """True when the model's held-out MAE improves on the naive baseline."""
        return self.model.mae < self.baseline.mae

    def run_record(self) -> dict[str, Any]:
        """A flat record of the run for experiment logging (#56)."""
        return {
            "model": "HistGradientBoostingRegressor",
            "n_train": self.n_train,
            "n_test": self.n_test,
            "n_features": len(self.features),
            "baseline": asdict(self.baseline),
            "metrics": asdict(self.model),
            "beats_baseline": self.beats_baseline,
        }


def train_lap_regressor(
    laps: pd.DataFrame, *, test_size: float = 0.25, random_state: int = 0
) -> LapRegressionResult:
    """Train + evaluate lap-time regression on a leakage-free, driver-grouped split."""
    features, target = lap_features(laps)
    # Driver labels aligned to the feature rows (lap_features uses the same order).
    groups = clean_laps(laps).sort_values(["Driver", "LapNumber"]).reset_index(drop=True)["Driver"]

    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(splitter.split(features, target, groups))
    x_train, x_test = features.iloc[train_idx], features.iloc[test_idx]
    y_train, y_test = target.iloc[train_idx], target.iloc[test_idx]

    # Naive baseline: predict the training mean for every held-out lap.
    baseline = evaluate(y_test, [y_train.mean()] * len(y_test))

    regressor = HistGradientBoostingRegressor(random_state=random_state)
    regressor.fit(x_train, y_train)
    model = evaluate(y_test, regressor.predict(x_test))

    result = LapRegressionResult(
        baseline=baseline,
        model=model,
        n_train=len(x_train),
        n_test=len(x_test),
        features=list(features.columns),
    )
    _logger.info("lap regression run: %s", result.run_record())
    return result
