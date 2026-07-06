"""Tests for the cross-validated evaluation/comparison harness (#54)."""

import pandas as pd
from sklearn.dummy import DummyRegressor

from ml import compare_classification, compare_regression, cross_val_scores


def _regression_laps() -> pd.DataFrame:
    """15 drivers × 20 laps; lap time is a driver-independent function of tyre age.

    Enough rows that the gradient-boosting model (min_samples_leaf defaults to 20)
    can actually split and learn the signal, so it beats the mean baseline under CV.
    """
    rows = []
    for d in range(15):
        for tyre in range(1, 21):
            secs = 92.0 + 0.3 * tyre  # strong, clean tyre-age signal
            rows.append(
                {
                    "Driver": f"D{d}",
                    "LapNumber": tyre,
                    "LapTime": pd.to_timedelta(secs, unit="s"),
                    "Stint": 1,
                    "TyreLife": tyre,
                    "Compound": "MEDIUM",
                }
            )
    return pd.DataFrame(rows)


def _classification_laps() -> pd.DataFrame:
    """12 drivers, a long HARD and a short SOFT stint each."""
    rows = []
    for d in range(12):
        for stint, compound, n, pace in ((1, "HARD", 20, 96.0), (2, "SOFT", 8, 94.0)):
            base = 0 if stint == 1 else 20
            for i in range(1, n + 1):
                rows.append(
                    {
                        "Driver": f"D{d}",
                        "LapNumber": base + i,
                        "LapTime": pd.to_timedelta(pace + i * 0.01, unit="s"),
                        "Stint": stint,
                        "Compound": compound,
                    }
                )
    return pd.DataFrame(rows)


def test_cross_val_scores_flips_negative_scorers() -> None:
    x = pd.DataFrame({"f": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]})
    y = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    groups = pd.Series(["a", "a", "b", "b", "c", "c"])
    scores = cross_val_scores(
        DummyRegressor(strategy="mean"),
        x,
        y,
        groups,
        {"MAE": "neg_mean_absolute_error"},
        n_splits=3,
    )
    assert "MAE" in scores and scores["MAE"] >= 0  # sign flipped to positive


def test_compare_regression_table() -> None:
    table = compare_regression(_regression_laps(), n_splits=3)
    assert list(table["model"]) == ["baseline (mean)", "gradient boosting"]
    assert set(table.columns) == {"model", "MAE", "RMSE", "R2"}
    mae = dict(zip(table["model"], table["MAE"], strict=True))
    assert mae["gradient boosting"] < mae["baseline (mean)"]  # model wins on MAE


def test_compare_classification_table() -> None:
    table = compare_classification(_classification_laps(), n_splits=3)
    assert list(table["model"]) == ["baseline (majority)", "random forest"]
    assert set(table.columns) == {"model", "Accuracy", "F1_macro"}
    f1 = dict(zip(table["model"], table["F1_macro"], strict=True))
    assert f1["random forest"] >= f1["baseline (majority)"]


def test_both_tasks_use_the_same_harness() -> None:
    # Consistency: both comparison tables have a baseline + model row.
    assert len(compare_regression(_regression_laps(), n_splits=3)) == 2
    assert len(compare_classification(_classification_laps(), n_splits=3)) == 2
