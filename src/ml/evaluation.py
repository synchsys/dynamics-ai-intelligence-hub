"""Consistent, cross-validated model evaluation and comparison (#54).

One harness — ``cross_val_scores`` over a driver-grouped ``GroupKFold`` — is
applied to both the regression (#49) and classification (#52) models so results
are comparable and reproducible. ``compare_regression`` / ``compare_classification``
produce a model-vs-baseline table with the same metrics per task. Cross-validation
gives a more robust estimate than a single split, and the driver grouping keeps
every fold leakage-free. Metric choices are documented in
``docs/architecture/model-evaluation.md``.
"""

from typing import Any

import pandas as pd
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestClassifier
from sklearn.model_selection import GroupKFold, cross_validate

from fastf1_analytics.analysis import clean_laps
from ml.features import lap_features, race_context_features
from shared.logging import get_logger

_logger = get_logger("ml.evaluation")

# display name -> sklearn scorer (neg_* scorers are sign-flipped to positive)
_REGRESSION_SCORING = {
    "MAE": "neg_mean_absolute_error",
    "RMSE": "neg_root_mean_squared_error",
    "R2": "r2",
}
_CLASSIFICATION_SCORING = {"Accuracy": "accuracy", "F1_macro": "f1_macro"}


def cross_val_scores(
    estimator: Any,
    features: pd.DataFrame,
    target: "pd.Series[Any]",
    groups: "pd.Series[Any]",
    scoring: dict[str, str],
    *,
    n_splits: int = 5,
) -> dict[str, float]:
    """Mean cross-validated score per metric, using group-aware K-fold.

    ``neg_*`` sklearn scorers are returned as positive values (so MAE/RMSE read
    naturally). Folds are grouped so no group spans train and test.
    """
    cv = GroupKFold(n_splits=n_splits)
    results = cross_validate(estimator, features, target, groups=groups, scoring=scoring, cv=cv)
    scores: dict[str, float] = {}
    for name, scorer in scoring.items():
        mean = float(results[f"test_{name}"].mean())
        scores[name] = round(-mean if scorer.startswith("neg_") else mean, 4)
    return scores


def _lap_groups(laps: pd.DataFrame) -> "pd.Series[Any]":
    return clean_laps(laps).sort_values(["Driver", "LapNumber"]).reset_index(drop=True)["Driver"]


def _stint_groups(laps: pd.DataFrame) -> "pd.Series[Any]":
    return clean_laps(laps).groupby(["Driver", "Stint"], as_index=False).size()["Driver"]


def compare_regression(
    laps: pd.DataFrame, *, n_splits: int = 5, random_state: int = 0
) -> pd.DataFrame:
    """Cross-validated regression comparison: baseline (mean) vs gradient boosting."""
    features, target = lap_features(laps)
    groups = _lap_groups(laps)
    models = {
        "baseline (mean)": DummyRegressor(strategy="mean"),
        "gradient boosting": HistGradientBoostingRegressor(random_state=random_state),
    }
    rows = [
        {
            "model": name,
            **cross_val_scores(
                est, features, target, groups, _REGRESSION_SCORING, n_splits=n_splits
            ),
        }
        for name, est in models.items()
    ]
    return pd.DataFrame(rows)


def compare_classification(
    laps: pd.DataFrame, *, n_splits: int = 5, random_state: int = 0
) -> pd.DataFrame:
    """Cross-validated classification comparison: majority baseline vs random forest."""
    features, target = race_context_features(laps)
    groups = _stint_groups(laps)
    models = {
        "baseline (majority)": DummyClassifier(strategy="most_frequent"),
        "random forest": RandomForestClassifier(random_state=random_state),
    }
    rows = [
        {
            "model": name,
            **cross_val_scores(
                est, features, target, groups, _CLASSIFICATION_SCORING, n_splits=n_splits
            ),
        }
        for name, est in models.items()
    ]
    return pd.DataFrame(rows)
