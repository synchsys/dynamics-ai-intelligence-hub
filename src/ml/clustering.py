"""Clustering analysis — the unsupervised workflow (#53).

Clusters stint profiles (from the race-context features, #51): scale features,
choose ``k`` by silhouette score, fit KMeans, and summarise each cluster so the
groups can be interpreted. Deterministic given ``random_state``; pure
sklearn/pandas so it is unit-testable. A thin notebook + doc interpret the live
clusters.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from shared.logging import get_logger

_logger = get_logger("ml.clustering")

DEFAULT_K_RANGE = range(2, 7)


@dataclass(frozen=True)
class ClusterResult:
    """A fitted clustering with the labels and a per-cluster summary."""

    k: int
    silhouette: float
    labels: list[int]
    summary: pd.DataFrame  # per-cluster feature means + Size
    k_scores: dict[int, float]  # silhouette per candidate k (empty if k was fixed)


def choose_k(
    features_scaled: Any, k_range: Iterable[int], *, random_state: int = 0
) -> dict[int, float]:
    """Silhouette score for each candidate ``k`` (skipping k ≥ n_samples)."""
    n = len(features_scaled)
    scores: dict[int, float] = {}
    for k in k_range:
        if k >= n:
            continue
        labels = KMeans(n_clusters=k, random_state=random_state, n_init=10).fit_predict(
            features_scaled
        )
        scores[k] = round(float(silhouette_score(features_scaled, labels)), 4)
    return scores


def cluster_stints(
    features: pd.DataFrame,
    *,
    k: int | None = None,
    k_range: Iterable[int] = DEFAULT_K_RANGE,
    random_state: int = 0,
) -> ClusterResult:
    """Scale, (optionally choose k), fit KMeans, and summarise the clusters."""
    scaled = StandardScaler().fit_transform(features)

    scores: dict[int, float] = {}
    if k is None:
        scores = choose_k(scaled, k_range, random_state=random_state)
        if not scores:
            raise ValueError("no valid k in k_range for this dataset size")
        k = max(scores, key=lambda key: scores[key])

    labels = KMeans(n_clusters=k, random_state=random_state, n_init=10).fit_predict(scaled)
    silhouette = round(float(silhouette_score(scaled, labels)), 4)

    labelled = features.copy()
    labelled["Cluster"] = labels
    summary = labelled.groupby("Cluster").mean().round(3)
    summary["Size"] = labelled.groupby("Cluster").size()

    _logger.info("clustered %d rows into k=%d (silhouette=%.3f)", len(features), k, silhouette)
    return ClusterResult(
        k=k, silhouette=silhouette, labels=labels.tolist(), summary=summary, k_scores=scores
    )


def plot_clusters(
    features: pd.DataFrame, labels: list[int], *, x: str, y: str, ax: Axes | None = None
) -> Axes:
    """Scatter two feature columns coloured by cluster label."""
    if ax is None:
        _fig, ax = plt.subplots()
    scatter = ax.scatter(features[x], features[y], c=labels, cmap="viridis")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title("Stint clusters")
    ax.figure.colorbar(scatter, ax=ax, label="Cluster")
    return ax
