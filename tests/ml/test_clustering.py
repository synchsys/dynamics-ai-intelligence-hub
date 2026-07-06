"""Tests for clustering analysis (deterministic, two well-separated blobs)."""

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from sklearn.preprocessing import StandardScaler

from ml import ClusterResult, choose_k, cluster_stints, plot_clusters


def _blobs() -> pd.DataFrame:
    """Two clearly separated groups of stint profiles (10 rows each)."""
    rows = []
    for i in range(10):
        j = i * 0.1
        rows.append(
            {"StartLap": 1 + j, "StintLength": 20 + j, "AvgPace": 95 + j, "BestPace": 94 + j}
        )
        rows.append(
            {"StartLap": 30 + j, "StintLength": 8 + j, "AvgPace": 105 + j, "BestPace": 104 + j}
        )
    return pd.DataFrame(rows)


def test_choose_k_prefers_two_for_two_blobs() -> None:
    scaled = StandardScaler().fit_transform(_blobs())
    scores = choose_k(scaled, range(2, 6))
    assert set(scores) == {2, 3, 4, 5}
    assert max(scores, key=lambda k: scores[k]) == 2  # two blobs → k=2 wins


def test_choose_k_skips_k_at_or_above_n() -> None:
    scaled = StandardScaler().fit_transform(_blobs().head(3))
    scores = choose_k(scaled, range(2, 6))  # n=3 → only k=2 valid
    assert set(scores) == {2}


def test_cluster_stints_finds_two_groups() -> None:
    result = cluster_stints(_blobs(), random_state=0)
    assert isinstance(result, ClusterResult)
    assert result.k == 2
    assert result.silhouette > 0.5  # well-separated
    assert len(set(result.labels)) == 2
    assert len(result.summary) == 2
    assert result.summary["Size"].sum() == 20


def test_cluster_stints_summary_separates_pace() -> None:
    result = cluster_stints(_blobs(), random_state=0)
    # The two clusters should differ markedly in average pace.
    paces = sorted(result.summary["AvgPace"])
    assert paces[1] - paces[0] > 5


def test_cluster_stints_explicit_k_skips_selection() -> None:
    result = cluster_stints(_blobs(), k=3, random_state=0)
    assert result.k == 3 and len(result.summary) == 3
    assert result.k_scores == {}  # k was fixed, no search


def test_cluster_stints_raises_when_no_valid_k() -> None:
    with pytest.raises(ValueError, match="no valid k"):
        cluster_stints(_blobs().head(2), k_range=range(3, 5))


def test_plot_clusters_returns_axes_with_points() -> None:
    result = cluster_stints(_blobs(), random_state=0)
    ax = plot_clusters(_blobs(), result.labels, x="AvgPace", y="StintLength")
    assert ax.get_xlabel() == "AvgPace" and ax.get_ylabel() == "StintLength"
    assert len(ax.collections) >= 1  # the scatter
    plt.close("all")


def test_plot_clusters_uses_supplied_axes() -> None:
    result = cluster_stints(_blobs(), random_state=0)
    _fig, ax = plt.subplots()
    assert plot_clusters(_blobs(), result.labels, x="AvgPace", y="BestPace", ax=ax) is ax
    plt.close("all")
