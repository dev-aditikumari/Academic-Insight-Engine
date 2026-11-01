"""Statistics used by the report."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .schema import SCORE_COLUMNS

# At-risk rule: a student is flagged when at least MIN_SIGNALS of these hold.
# All comparisons are strict, so a value exactly on the threshold is not a signal.
ATTENDANCE_THRESHOLD = 75.0
STUDY_HOURS_THRESHOLD = 5.0
PREVIOUS_GRADE_THRESHOLD = 60.0
MIN_SIGNALS = 2

PREDICTORS = ["StudyHours", "AttendanceRate", "PreviousGrade", "ParentalSupport"]


def describe_scores(df: pd.DataFrame) -> pd.DataFrame:
    columns = [*SCORE_COLUMNS, "AverageScore"]
    return df[columns].describe().T[["count", "mean", "std", "min", "50%", "max"]]


def score_correlations(
    df: pd.DataFrame, predictors: list[str] | None = None, target: str = "AverageScore"
) -> pd.Series:
    """Pearson correlation of each predictor with the target, strongest first."""
    predictors = predictors or PREDICTORS
    corr = df[predictors].corrwith(df[target])
    return corr.reindex(corr.abs().sort_values(ascending=False).index)


def group_means(df: pd.DataFrame, by: str, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns or SCORE_COLUMNS
    return df.groupby(by, observed=True)[columns].mean()


def pass_rate_by(df: pd.DataFrame, by: str) -> pd.Series:
    return df.groupby(by, observed=True)["Passed"].mean()


def at_risk_signals(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "LowAttendance": df["AttendanceRate"] < ATTENDANCE_THRESHOLD,
            "LowStudyHours": df["StudyHours"] < STUDY_HOURS_THRESHOLD,
            "LowPreviousGrade": df["PreviousGrade"] < PREVIOUS_GRADE_THRESHOLD,
        },
        index=df.index,
    )


def flag_at_risk(df: pd.DataFrame) -> pd.Series:
    """True where at least MIN_SIGNALS of the three risk signals are present."""
    return at_risk_signals(df).sum(axis=1) >= MIN_SIGNALS


def at_risk_summary(df: pd.DataFrame) -> dict[str, float]:
    flagged = flag_at_risk(df)
    summary = {
        "students": int(len(df)),
        "at_risk": int(flagged.sum()),
        "at_risk_share": float(flagged.mean()),
    }
    if "Passed" in df.columns:
        summary["fail_rate_at_risk"] = (
            float(1 - df.loc[flagged, "Passed"].mean()) if flagged.any() else float("nan")
        )
        summary["fail_rate_not_at_risk"] = (
            float(1 - df.loc[~flagged, "Passed"].mean()) if (~flagged).any() else float("nan")
        )
    return summary


def fit_linear_regression(
    df: pd.DataFrame, features: list[str] | None = None, target: str = "AverageScore"
) -> dict:
    """Ordinary least squares with an intercept, solved with numpy."""
    features = features or PREDICTORS
    x = df[features].to_numpy(dtype=float)
    y = df[target].to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    predicted = design @ beta
    ss_res = float(((y - predicted) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {
        "intercept": float(beta[0]),
        "coefficients": dict(zip(features, (float(b) for b in beta[1:]), strict=True)),
        "r2": r2,
    }
