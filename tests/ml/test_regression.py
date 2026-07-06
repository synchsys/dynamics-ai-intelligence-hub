"""Tests for lap-time regression (synthetic data, deterministic)."""

import pandas as pd

from ml import RegressionMetrics, evaluate, train_lap_regressor

_COMPOUND_OFFSET = {"SOFT": -0.5, "MEDIUM": 0.0, "HARD": 0.5}


def _synthetic_laps() -> pd.DataFrame:
    """8 drivers; lap time is a driver-independent function of tyre age/lap/compound.

    Because the signal is shared across drivers, a model can learn it and beat the
    train-mean baseline even on held-out (grouped-out) drivers.
    """
    rows = []
    for d in range(8):
        for stint, compound in ((1, "MEDIUM"), (2, "SOFT")):
            for tyre_life in range(1, 6):
                lap_number = (stint - 1) * 5 + tyre_life
                seconds = 95.0 + 0.15 * tyre_life - 0.02 * lap_number + _COMPOUND_OFFSET[compound]
                rows.append(
                    {
                        "Driver": f"D{d}",
                        "LapNumber": lap_number,
                        "LapTime": pd.to_timedelta(seconds, unit="s"),
                        "Stint": stint,
                        "TyreLife": tyre_life,
                        "Compound": compound,
                    }
                )
    return pd.DataFrame(rows)


# --- evaluate ---------------------------------------------------------------


def test_evaluate_perfect_prediction() -> None:
    m = evaluate([90.0, 95.0, 100.0], [90.0, 95.0, 100.0])
    assert m == RegressionMetrics(mae=0.0, rmse=0.0, r2=1.0)


def test_evaluate_known_values() -> None:
    m = evaluate([10.0, 20.0], [12.0, 18.0])  # errors +2, -2
    assert m.mae == 2.0 and m.rmse == 2.0


# --- training ---------------------------------------------------------------


def test_model_beats_baseline_on_grouped_holdout() -> None:
    result = train_lap_regressor(_synthetic_laps(), random_state=0)
    assert result.beats_baseline
    assert result.model.mae < result.baseline.mae
    assert result.model.r2 > 0.8  # strong learnable signal
    assert result.n_train + result.n_test == 80  # every lap used exactly once
    assert result.n_test > 0


def test_result_is_deterministic() -> None:
    a = train_lap_regressor(_synthetic_laps(), random_state=0)
    b = train_lap_regressor(_synthetic_laps(), random_state=0)
    assert a.model == b.model and a.baseline == b.baseline


def test_run_record_has_expected_shape() -> None:
    record = train_lap_regressor(_synthetic_laps(), random_state=0).run_record()
    assert record["model"] == "HistGradientBoostingRegressor"
    assert record["beats_baseline"] is True
    assert set(record) == {
        "model",
        "n_train",
        "n_test",
        "n_features",
        "baseline",
        "metrics",
        "beats_baseline",
    }
    assert record["metrics"]["mae"] < record["baseline"]["mae"]
