"""Strategy classification — the supervised classification workflow (#52).

Predicts a stint's tyre **compound** (the strategy label) from the race-context
features (#51) with a random forest, against a majority-class baseline, on a
leakage-free split grouped by driver. Reports accuracy, macro-F1, and a confusion
matrix. Deterministic given ``random_state``; pure sklearn/pandas so it is
unit-testable on synthetic data. ``scripts/ml/train_strategy_classifier.py`` runs
it on a live session.
"""

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GroupShuffleSplit

from fastf1_analytics.analysis import clean_laps
from ml.features import race_context_features
from shared.logging import get_logger

_logger = get_logger("ml.classification")


@dataclass(frozen=True)
class ClassificationMetrics:
    """Held-out classification metrics."""

    accuracy: float
    f1_macro: float
    labels: list[str]
    confusion: list[list[int]]


def evaluate_classification(y_true: Any, y_pred: Any) -> ClassificationMetrics:
    labels = sorted(set(map(str, y_true)) | set(map(str, y_pred)))
    return ClassificationMetrics(
        accuracy=round(float(accuracy_score(y_true, y_pred)), 4),
        f1_macro=round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        labels=labels,
        confusion=confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    )


@dataclass(frozen=True)
class StrategyClassificationResult:
    baseline: ClassificationMetrics
    model: ClassificationMetrics
    n_train: int
    n_test: int
    classes: list[str]

    @property
    def beats_baseline(self) -> bool:
        """True when the model's macro-F1 improves on the majority-class baseline."""
        return self.model.f1_macro > self.baseline.f1_macro

    def run_record(self) -> dict[str, Any]:
        return {
            "model": "RandomForestClassifier",
            "n_train": self.n_train,
            "n_test": self.n_test,
            "classes": self.classes,
            "baseline": asdict(self.baseline),
            "metrics": asdict(self.model),
            "beats_baseline": self.beats_baseline,
        }


def train_strategy_classifier(
    laps: pd.DataFrame, *, test_size: float = 0.25, random_state: int = 0
) -> StrategyClassificationResult:
    """Train + evaluate compound classification on a driver-grouped, leakage-free split."""
    features, target = race_context_features(laps)
    groups = (
        clean_laps(laps).groupby(["Driver", "Stint"], as_index=False).size()["Driver"]
    )  # aligned with the per-stint feature rows

    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(splitter.split(features, target, groups))
    x_train, x_test = features.iloc[train_idx], features.iloc[test_idx]
    y_train, y_test = target.iloc[train_idx], target.iloc[test_idx]

    baseline_pred = DummyClassifier(strategy="most_frequent").fit(x_train, y_train).predict(x_test)
    baseline = evaluate_classification(y_test, baseline_pred)

    model_pred = (
        RandomForestClassifier(random_state=random_state).fit(x_train, y_train).predict(x_test)
    )
    model = evaluate_classification(y_test, model_pred)

    result = StrategyClassificationResult(
        baseline=baseline,
        model=model,
        n_train=len(x_train),
        n_test=len(x_test),
        classes=sorted(set(map(str, target))),
    )
    _logger.info("strategy classification run: %s", result.run_record())
    return result
