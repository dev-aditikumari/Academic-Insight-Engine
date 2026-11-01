"""Derived columns: average score, pass flag, performance and attendance bands."""

from __future__ import annotations

import pandas as pd

from .schema import SCORE_COLUMNS

PASS_MARK = 50.0
PERFORMANCE_BINS = [-float("inf"), PASS_MARK, 65.0, 80.0, float("inf")]
PERFORMANCE_LABELS = ["Fail", "Satisfactory", "Good", "Excellent"]
ATTENDANCE_BINS = [-float("inf"), 75.0, 90.0, float("inf")]
ATTENDANCE_LABELS = ["Low", "Medium", "High"]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with AverageScore, Passed, PerformanceBand and AttendanceBand.

    Bands use left-closed intervals: an average of exactly 50 is Satisfactory,
    exactly 65 is Good, exactly 80 is Excellent. Attendance of exactly 75 is
    Medium and exactly 90 is High.
    """
    out = df.copy()
    out["AverageScore"] = out[SCORE_COLUMNS].mean(axis=1)
    out["Passed"] = out["AverageScore"] >= PASS_MARK
    out["PerformanceBand"] = pd.cut(
        out["AverageScore"], PERFORMANCE_BINS, labels=PERFORMANCE_LABELS, right=False
    )
    out["AttendanceBand"] = pd.cut(
        out["AttendanceRate"], ATTENDANCE_BINS, labels=ATTENDANCE_LABELS, right=False
    )
    return out
