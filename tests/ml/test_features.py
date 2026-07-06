"""Tests for the three portfolio feature sets (#51)."""

import pandas as pd

from ml import AUDIT_FEATURES, audit_features, lap_features, race_context_features


def _laps() -> pd.DataFrame:
    td = pd.to_timedelta
    return pd.DataFrame(
        {
            "Driver": ["HAM", "HAM", "HAM", "VER", "VER"],
            "LapNumber": [1, 2, 3, 1, 2],
            "LapTime": [td("0:01:36"), td("0:01:35"), td("0:01:34"), td("0:01:35"), td("0:01:34")],
            "Stint": [1, 1, 1, 1, 1],
            "TyreLife": [1, 2, 3, 5, 6],
            "Compound": ["MEDIUM", "MEDIUM", "MEDIUM", "SOFT", "SOFT"],
        }
    )


# --- lap features -----------------------------------------------------------


def test_lap_features_shape_and_target() -> None:
    x, y = lap_features(_laps())
    assert len(x) == len(y) == 5
    assert list(y) == [96.0, 95.0, 94.0, 95.0, 94.0]  # target = LapTimeSeconds
    assert "LapTimeSeconds" not in x.columns  # target never leaks into features
    assert {"LapNumber", "Stint", "StintLap", "TyreLife"} <= set(x.columns)
    assert {"Comp_MEDIUM", "Comp_SOFT"} <= set(x.columns)


def test_lap_features_stint_lap_counter() -> None:
    x, _ = lap_features(_laps())
    ham = x[x["TyreLife"].isin([1, 2, 3])]
    assert ham["StintLap"].tolist() == [1, 2, 3]  # position within the stint


def test_lap_features_derives_tyrelife_when_absent() -> None:
    laps = _laps().drop(columns=["TyreLife"])
    x, _ = lap_features(laps)
    # TyreLife falls back to StintLap (both 1..n within a stint).
    assert x["TyreLife"].tolist() == x["StintLap"].tolist()


# --- race-context features --------------------------------------------------


def test_race_context_features_per_stint() -> None:
    x, y = race_context_features(_laps())
    assert len(x) == len(y) == 2  # one row per driver+stint
    assert set(y) == {"MEDIUM", "SOFT"}  # target = compound
    assert "Compound" not in x.columns
    assert list(x.columns) == ["StartLap", "StintLength", "AvgPace", "BestPace", "PaceRange"]
    assert len(x.columns) >= 5


def test_race_context_values() -> None:
    x, y = race_context_features(_laps())
    ham = x[y == "MEDIUM"].iloc[0]
    assert ham["StintLength"] == 3 and ham["StartLap"] == 1
    assert ham["BestPace"] == 94.0 and ham["PaceRange"] == 2.0  # 96 - 94


# --- audit features ---------------------------------------------------------


def _events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "EntityId": ["E1", "E1", "E1", "E2", "E1"],
            "Actor": ["u1", "u2", "u1", "u3", "u9"],
            "ChangedOn": [
                "2026-01-01",
                "2026-01-05",
                "2026-01-09",
                "2026-01-02",
                "2026-02-01",  # after the cutoff below — must be excluded
            ],
        }
    )


def test_audit_features_columns_and_cutoff() -> None:
    feats = audit_features(_events(), as_of="2026-01-10")
    assert list(feats.columns) == AUDIT_FEATURES
    assert len(AUDIT_FEATURES) >= 5
    e1 = feats.loc["E1"]
    assert e1["ChangeCount"] == 3  # the 2026-02-01 event is excluded (after as_of)
    assert e1["DistinctActors"] == 2  # u1, u2 (u9 event excluded)
    assert e1["RecencyDays"] == 1  # last kept change 2026-01-09 vs cutoff 2026-01-10
    assert e1["ChangesLast7d"] == 2  # 01-05 and 01-09 within 7 days of cutoff


def test_audit_features_excludes_future_events() -> None:
    # With a cutoff before E1's later activity, only the first event counts.
    feats = audit_features(_events(), as_of="2026-01-01")
    assert feats.loc["E1"]["ChangeCount"] == 1
    assert "E2" not in feats.index  # E2's only event is after this cutoff
