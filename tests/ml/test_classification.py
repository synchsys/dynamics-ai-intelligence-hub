"""Tests for strategy (compound) classification (synthetic, deterministic)."""

import pandas as pd

from ml import ClassificationMetrics, evaluate_classification, train_strategy_classifier


def _synthetic_laps() -> pd.DataFrame:
    """12 drivers, two stints each: a long HARD stint and a short SOFT stint.

    Compound is cleanly determined by stint length/pace, so a classifier learns it
    and beats a majority-class baseline; both classes appear in every driver.
    """
    rows = []
    for d in range(12):
        for stint, compound, laps_in_stint, pace in ((1, "HARD", 20, 96.0), (2, "SOFT", 8, 94.0)):
            base_lap = 0 if stint == 1 else 20
            for i in range(1, laps_in_stint + 1):
                rows.append(
                    {
                        "Driver": f"D{d}",
                        "LapNumber": base_lap + i,
                        "LapTime": pd.to_timedelta(pace + i * 0.01, unit="s"),
                        "Stint": stint,
                        "Compound": compound,
                    }
                )
    return pd.DataFrame(rows)


def test_evaluate_classification_known_values() -> None:
    m = evaluate_classification(["A", "A", "B"], ["A", "B", "B"])
    assert m.labels == ["A", "B"]
    assert m.accuracy == round(2 / 3, 4)
    # confusion: A row [1 correct, 1 as B]; B row [0, 1 correct]
    assert m.confusion == [[1, 1], [0, 1]]


def test_perfect_classification_metrics() -> None:
    m = evaluate_classification(["SOFT", "HARD"], ["SOFT", "HARD"])
    assert m.accuracy == 1.0 and m.f1_macro == 1.0


def test_model_beats_majority_baseline() -> None:
    result = train_strategy_classifier(_synthetic_laps(), random_state=0)
    assert result.beats_baseline
    assert result.model.f1_macro > result.baseline.f1_macro
    assert result.model.accuracy > 0.8  # clean learnable signal
    assert result.n_train + result.n_test == 24  # one row per driver+stint
    assert set(result.classes) == {"HARD", "SOFT"}


def test_confusion_matrix_is_square_over_labels() -> None:
    result = train_strategy_classifier(_synthetic_laps(), random_state=0)
    m = result.model
    assert len(m.confusion) == len(m.labels)
    assert all(len(row) == len(m.labels) for row in m.confusion)


def test_result_is_deterministic() -> None:
    a = train_strategy_classifier(_synthetic_laps(), random_state=0)
    b = train_strategy_classifier(_synthetic_laps(), random_state=0)
    assert a.model == b.model and a.baseline == b.baseline


def test_run_record_shape() -> None:
    record = train_strategy_classifier(_synthetic_laps(), random_state=0).run_record()
    assert record["model"] == "RandomForestClassifier"
    assert record["beats_baseline"] is True
    assert isinstance(record["metrics"], dict) and "f1_macro" in record["metrics"]


def test_metrics_dataclass_shape() -> None:
    m = ClassificationMetrics(accuracy=1.0, f1_macro=1.0, labels=["A"], confusion=[[1]])
    assert m.labels == ["A"]
