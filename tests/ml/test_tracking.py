"""Tests for the experiment tracker (JSONL runs)."""

from pathlib import Path

from ml import DEFAULT_SEED, ExperimentTracker, RunRecord


def test_log_run_writes_and_reads_back(tmp_path: Path) -> None:
    tracker = ExperimentTracker(tmp_path / "runs.jsonl")
    rec = tracker.log_run("regression", params={"model": "gbr"}, metrics={"mae": 1.5}, seed=0)
    assert rec == RunRecord("regression", {"model": "gbr"}, {"mae": 1.5}, 0)
    runs = tracker.runs()
    assert len(runs) == 1 and runs[0].metrics["mae"] == 1.5


def test_runs_append_in_order(tmp_path: Path) -> None:
    tracker = ExperimentTracker(tmp_path / "runs.jsonl")
    tracker.log_run("a", metrics={"mae": 2.0})
    tracker.log_run("b", metrics={"mae": 1.0})
    assert [r.name for r in tracker.runs()] == ["a", "b"]


def test_runs_empty_when_no_file(tmp_path: Path) -> None:
    assert ExperimentTracker(tmp_path / "none.jsonl").runs() == []


def test_default_seed_is_used(tmp_path: Path) -> None:
    rec = ExperimentTracker(tmp_path / "r.jsonl").log_run("x")
    assert rec.seed == DEFAULT_SEED and rec.params == {} and rec.metrics == {}


def test_best_run_min_and_max(tmp_path: Path) -> None:
    tracker = ExperimentTracker(tmp_path / "runs.jsonl")
    tracker.log_run("a", metrics={"mae": 2.0, "r2": 0.7})
    tracker.log_run("b", metrics={"mae": 1.0, "r2": 0.9})
    tracker.log_run("c", metrics={"other": 5.0})  # missing the metric — ignored
    best_mae = tracker.best("mae")
    best_r2 = tracker.best("r2", minimize=False)
    assert best_mae is not None and best_mae.name == "b"  # lowest MAE
    assert best_r2 is not None and best_r2.name == "b"  # highest R2


def test_best_none_when_metric_absent(tmp_path: Path) -> None:
    tracker = ExperimentTracker(tmp_path / "runs.jsonl")
    tracker.log_run("a", metrics={"mae": 1.0})
    assert tracker.best("nonexistent") is None


def test_record_json_round_trip() -> None:
    rec = RunRecord("run", {"k": 5}, {"silhouette": 0.49}, seed=7)
    import json

    assert RunRecord.from_dict(json.loads(rec.to_json())) == rec


def test_reproducibility_same_seed_same_metrics(tmp_path: Path) -> None:
    # Two runs of a deterministic model at the same seed log identical metrics.
    import pandas as pd

    from ml import train_lap_regressor

    rows = []
    for d in range(6):
        for tyre in range(1, 6):
            secs = 95.0 + 0.2 * tyre
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
    laps = pd.DataFrame(rows)
    tracker = ExperimentTracker(tmp_path / "runs.jsonl")
    for _ in range(2):
        result = train_lap_regressor(laps, random_state=DEFAULT_SEED)
        tracker.log_run("lap-regression", metrics=result.model.__dict__, seed=DEFAULT_SEED)
    a, b = tracker.runs()
    assert a.metrics == b.metrics  # re-running with the fixed seed reproduces the metrics
