"""Machine-learning pillar (Epic 7): feature sets and portfolio models."""

from ml.classification import (
    ClassificationMetrics,
    StrategyClassificationResult,
    evaluate_classification,
    train_strategy_classifier,
)
from ml.clustering import ClusterResult, choose_k, cluster_stints, plot_clusters
from ml.features import (
    AUDIT_FEATURES,
    LAP_NUMERIC_FEATURES,
    audit_features,
    lap_features,
    race_context_features,
)
from ml.regression import (
    LapRegressionResult,
    RegressionMetrics,
    evaluate,
    train_lap_regressor,
)
from ml.tracking import DEFAULT_SEED, ExperimentTracker, RunRecord

__all__ = [
    # features (#51)
    "lap_features",
    "race_context_features",
    "audit_features",
    "LAP_NUMERIC_FEATURES",
    "AUDIT_FEATURES",
    # regression (#49)
    "train_lap_regressor",
    "evaluate",
    "RegressionMetrics",
    "LapRegressionResult",
    # clustering (#53)
    "cluster_stints",
    "choose_k",
    "plot_clusters",
    "ClusterResult",
    # experiment tracking (#56)
    "ExperimentTracker",
    "RunRecord",
    "DEFAULT_SEED",
    # classification (#52)
    "train_strategy_classifier",
    "evaluate_classification",
    "ClassificationMetrics",
    "StrategyClassificationResult",
]
