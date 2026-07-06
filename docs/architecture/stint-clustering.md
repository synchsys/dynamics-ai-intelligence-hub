# Stint clustering (unsupervised)

The unsupervised deliverable (#53, Epic 7): cluster race **stint profiles** into
strategy groups and interpret them. Built on the race-context features (#51) and
the tested `ml.clustering` helpers; the `notebooks/stint-clustering.ipynb`
notebook drives it thin.

## Method (`src/ml/clustering.py`)

1. **Features** — per-stint profiles from `race_context_features`: `StartLap`,
   `StintLength`, `AvgPace`, `BestPace`, `PaceRange`. Very short stints
   (`StintLength < 5` — a lap or two from an early retirement/red flag) are
   filtered out first, or they dominate the clustering as lone outliers.
2. **Scale** — `StandardScaler` (features are on different scales — laps vs
   seconds).
3. **Choose k** — `choose_k` computes the **silhouette score** for k = 2…6 and
   picks the best; `cluster_stints` then fits `KMeans` at that k. Deterministic
   given `random_state`.
4. **Summarise** — per-cluster feature means + size, for interpretation.

## Results (live — 2023 Singapore GP)

42 stint profiles (after filtering). Silhouette selected **k = 5**
(0.49, the best of `{2: 0.42, 3: 0.40, 4: 0.46, 5: 0.49, 6: 0.49}`). The clusters
separate primarily by **when the stint ran** (`StartLap`) and **how long it was**
(`StintLength`):

- **Opening stints** — start lap 1, medium length (the standard first stint).
- **Long stints** — ~40 laps: one-stop-style middle stints with high `PaceRange`
  (lots of tyre degradation).
- **Late / short stints** — high start lap, short length (final splash-and-dash
  or post-safety-car stints), some with the fastest `BestPace` on fresh tyres.

The silhouette (~0.5) reflects moderate, overlapping structure — realistic for
stint data, where strategies blend rather than form crisp groups.

## Limitations

- Single session; pooling races would give more stable, comparable clusters.
- KMeans assumes roughly spherical clusters; the short-stint filter is a manual
  cleaning step (a robust method or DBSCAN could handle outliers directly).
- Cluster *labels* are unstable across runs/sessions (KMeans numbering is
  arbitrary); interpret by the summary, not the cluster id.
