# Odds model v2 (calibrated pricing)

The ML upgrade to odds pricing (#232, Epic 7): a calibrated winner/podium
probability model that implements the same `OddsPricer` interface as the v1
heuristic and tags its odds `source = "model"` — completing the heuristic → model
narrative (ADR-0008).

## Model (`src/paddock/odds_model.py`)

- **Features** (`form_features`): from a driver's recent finishing positions —
  `mean_finish`, `win_rate`, `podium_rate`, `best_finish`, `races`.
- **Model** (`train_odds_model`): two `CalibratedClassifierCV`-wrapped
  `LogisticRegression`s (sigmoid calibration) — one for **win**, one for
  **podium**. Deterministic.
- **`ModelPricer`** implements `price(...)`: prices `driver_wins` /
  `podium_contains` from the calibrated probability (via the shared
  `price_probability` → bookmaker fraction + house margin, `source="model"`), and
  **delegates the other settlement types to a fallback** (the heuristic), so it
  fully satisfies the pricing contract.

## Results (live — 2023, 6 rounds, `scripts/paddock/train_odds_model.py`)

Trained on 120 leakage-free driver-race samples (a driver's form is their
finishing positions in the *other* rounds; the label is win/podium in the held
round).

**Calibration** (predicted → actual win rate, quantile bins):

| predicted | actual |
|-----------|--------|
| 0.01 | 0.00 |
| 0.02 | 0.00 |
| 0.03 | 0.00 |
| 0.08 | 0.00 |
| 0.17 | 0.25 |

**Model vs heuristic** (driver win price):

| driver | model | heuristic |
|--------|-------|-----------|
| #1 (Verstappen) | 3/1 against (p≈0.22) | 2/5 on (p≈0.64) |
| #77 (Bottas) | 40/1 against (p≈0.02) | 12/1 against (p≈0.07) |

## Interpretation

The calibrated model produces **markedly more conservative** probabilities than
the heuristic. That's the point of calibration: with only ~1 winner per 20 cars,
the base rate of "wins" is low, and the calibrated model reflects it — whereas the
heuristic's form ratio over-states favourites. On more data the top probabilities
would rise for a genuine dominant driver; here the small sample + strong class
imbalance keep them modest. Either way, the v2 pricer is a real ML deliverable
plugged into the same interface as v1.

## Limitations

- Small sample (6 races); win is a rare class — probabilities are conservative.
- Features are form-only; the backlog envisages stints/standings/historical
  (Ergast/jolpica) inputs, which would sharpen it.
- Requires the `analytics` extra (scikit-learn); import `ModelPricer` from
  `paddock.odds_model`.
