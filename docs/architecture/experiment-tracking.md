# Experiment tracking & reproducibility

Every portfolio-model result should be logged, comparable, and regenerable
(#56). This records the tracking approach, the seed policy, and how to reproduce
a run. Model cards live in [`model-cards/`](model-cards/).

## Approach: structured JSONL (not MLflow)

`src/ml/tracking.py` provides an `ExperimentTracker` that appends each run as one
JSON line (`name`, `params`, `metrics`, `seed`) to a runs file, with `runs()` to
read them back and `best(metric)` to compare.

**Why structured logging over MLflow:** it's dependency-free (no server, no extra
package), fully unit-tested, and matches the repo's hand-rolled style — enough to
log params/metrics/seeds and compare runs. A local MLflow could later slot in
behind the same `log_run` call if richer artefact/UI tracking is needed.

## Seed policy

A single `DEFAULT_SEED = 0` (`ml.tracking`) is threaded into every model's
`random_state` — the regression split + estimator (#49) and KMeans (#53). Because
those models are deterministic given `random_state`, re-running at the fixed seed
reproduces the metrics exactly. Any run that logs a different seed records it, so
results stay explainable.

## Reproducing a run

```bash
pip install -e ".[analytics]"
python scripts/ml/log_experiments.py
```

This logs (to `datasets/experiments/runs.jsonl`, git-ignored) two lap-time
regression runs and one clustering run, all at `DEFAULT_SEED`, and asserts the
two regression runs produce **identical** metrics. Verified live (2023 Singapore
GP):

| Run | Metrics (seed 0) |
|-----|------------------|
| lap-time-regression | MAE 1.5218, RMSE 3.4343, R² 0.8145 |
| lap-time-regression (re-run) | MAE 1.5218, RMSE 3.4343, R² 0.8145 |
| stint-clustering | silhouette 0.4919 |

Identical regression metrics across the two runs demonstrate fixed-seed
reproducibility.
