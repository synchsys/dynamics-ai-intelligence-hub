"""Documented, leakage-checked feature sets for the portfolio models (#51).

Three named sets, each a pandas transformer tied to a model:

* ``lap_features`` — per-lap features for lap-time regression (#49).
* ``race_context_features`` — per-stint features for strategy classification (#52).
* ``audit_features`` — per-entity change-frequency/recency features for audit
  anomaly detection (#55), computed as of a cutoff so no future information leaks.

The lap/race sets derive from a FastF1 laps table (via ``clean_laps``); the audit
set consumes the Epic 6 audit export (#48) — its transformer + tests run on a
fixture here and it wires to real data once that export exists. See
``docs/architecture/ml-features.md``.
"""

from typing import Any

import pandas as pd

from fastf1_analytics.analysis import clean_laps

# --- lap/stint features (target: LapTimeSeconds) ----------------------------

LAP_NUMERIC_FEATURES = ["LapNumber", "Stint", "StintLap", "TyreLife"]


def lap_features(laps: pd.DataFrame) -> tuple[pd.DataFrame, "pd.Series[float]"]:
    """Per-lap features + lap-time target for regression (#49).

    Leakage check: features are all known **at the start of the lap** (progress,
    stint position, tyre age, compound). Nothing derived from the lap's own time
    or from later laps is included; the target ``LapTimeSeconds`` is returned
    separately, never as a feature.
    """
    df = clean_laps(laps).sort_values(["Driver", "LapNumber"]).reset_index(drop=True)
    df["StintLap"] = df.groupby(["Driver", "Stint"]).cumcount() + 1
    if "TyreLife" not in df.columns:
        df["TyreLife"] = df["StintLap"]
    features = pd.get_dummies(
        df[[*LAP_NUMERIC_FEATURES, "Compound"]], columns=["Compound"], prefix="Comp"
    )
    return features, df["LapTimeSeconds"]


# --- race-context features (target: Compound) -------------------------------


def race_context_features(laps: pd.DataFrame) -> tuple[pd.DataFrame, "pd.Series[Any]"]:
    """Per-stint context features + compound target for strategy classification (#52).

    Leakage check: each row summarises one completed stint; the target is the
    stint's compound and is not among the features. Features describe *when* and
    *how* the stint ran, not which compound it was.
    """
    df = clean_laps(laps)
    grouped = df.groupby(["Driver", "Stint"], as_index=False).agg(
        StartLap=("LapNumber", "min"),
        StintLength=("LapNumber", "size"),
        AvgPace=("LapTimeSeconds", "mean"),
        BestPace=("LapTimeSeconds", "min"),
        Compound=("Compound", "first"),
    )
    grouped["PaceRange"] = (
        df.groupby(["Driver", "Stint"])["LapTimeSeconds"].max().to_numpy()
        - grouped["BestPace"].to_numpy()
    )
    target = grouped["Compound"]
    features = grouped[["StartLap", "StintLength", "AvgPace", "BestPace", "PaceRange"]].round(3)
    return features, target


# --- audit features (unsupervised; anomaly detection) -----------------------

AUDIT_FEATURES = [
    "ChangeCount",
    "DistinctActors",
    "RecencyDays",
    "ActiveSpanDays",
    "ChangesLast7d",
]


def audit_features(events: pd.DataFrame, *, as_of: pd.Timestamp | str) -> pd.DataFrame:
    """Per-entity change-frequency/recency features for anomaly detection (#55).

    ``events`` has columns ``EntityId``, ``Actor``, ``ChangedOn`` (the Epic 6
    audit export, #48). Leakage check: only events **at or before** ``as_of`` are
    used, so features never see the future; ``as_of`` is an explicit cutoff rather
    than "now" for reproducibility. Unsupervised — there is no target to leak.
    """
    cutoff = pd.Timestamp(as_of)
    ev = events.copy()
    ev["ChangedOn"] = pd.to_datetime(ev["ChangedOn"])
    ev = ev[ev["ChangedOn"] <= cutoff]

    grouped = ev.groupby("EntityId")
    feats = grouped.agg(
        ChangeCount=("ChangedOn", "size"),
        DistinctActors=("Actor", "nunique"),
        LastChange=("ChangedOn", "max"),
        FirstChange=("ChangedOn", "min"),
    )
    feats["RecencyDays"] = (cutoff - feats["LastChange"]).dt.days
    feats["ActiveSpanDays"] = (feats["LastChange"] - feats["FirstChange"]).dt.days
    week_ago = cutoff - pd.Timedelta("7D")
    feats["ChangesLast7d"] = grouped["ChangedOn"].apply(lambda s: int((s >= week_ago).sum()))
    return feats[AUDIT_FEATURES]
