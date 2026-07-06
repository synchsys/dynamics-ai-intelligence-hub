# Model card — stint clustering

## Overview
- **Task:** unsupervised clustering — group race stint profiles into strategy
  types.
- **Model:** `StandardScaler` → `KMeans` (scikit-learn), `random_state = 0`; k
  chosen by silhouette over k = 2…6.
- **Code:** `src/ml/clustering.py` (#53). **Seed:** `DEFAULT_SEED = 0`.

## Data & features
- **Data:** FastF1 laps for a session (dev: 2023 Singapore GP).
- **Features (#51):** per-stint `StartLap`, `StintLength`, `AvgPace`, `BestPace`,
  `PaceRange`. Stints shorter than 5 laps are filtered (they cluster as lone
  outliers). Unsupervised — no target.

## Result (2023 Singapore GP)
- 42 stint profiles → **k = 5** (silhouette **0.49**, best of
  `{2: 0.42, 3: 0.40, 4: 0.46, 5: 0.49, 6: 0.49}`).
- Clusters separate by *when* the stint ran and *how long* — opening stints, long
  high-degradation stints, and late/short splash stints.

## Intended use & limitations
- **Intended:** portfolio demonstration of an unsupervised workflow with
  principled k selection and interpreted clusters.
- **Not for:** definitive strategy labelling — silhouette ~0.5 reflects
  overlapping structure; cluster ids are arbitrary and unstable across runs
  (interpret by the per-cluster summary, not the id).
- Single session; KMeans assumes spherical clusters; the short-stint filter is a
  manual cleaning step.

## Reproduce
`python scripts/ml/log_experiments.py` at seed 0; see
`notebooks/stint-clustering.ipynb`.
