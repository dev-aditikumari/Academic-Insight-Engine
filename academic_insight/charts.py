"""Chart functions. Each saves a PNG and returns its path."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

from .analysis import fit_linear_regression, flag_at_risk, group_means  # noqa: E402
from .features import ATTENDANCE_LABELS, PERFORMANCE_LABELS  # noqa: E402
from .schema import PARENT_EDUC_LEVELS  # noqa: E402

BLUE = "#2F6690"
ORANGE = "#D1603D"
NOTE = "Synthetic data"


def _save(fig, out_dir: Path, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    fig.text(0.99, 0.01, NOTE, ha="right", va="bottom", fontsize=8, color="#666666")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def score_distribution(df, out_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(df["AverageScore"], bins=25, color=BLUE, ax=ax)
    ax.axvline(50, color=ORANGE, linestyle="--", label="Pass mark (50)")
    ax.set(title="Distribution of average score", xlabel="Average of math, reading, writing")
    ax.legend()
    return _save(fig, out_dir, "score_distribution.png")


def performance_bands(df, out_dir: Path) -> Path:
    counts = df["PerformanceBand"].value_counts().reindex(PERFORMANCE_LABELS)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(counts.index.astype(str), counts.to_numpy(), color=BLUE)
    ax.bar_label(ax.containers[0])
    ax.set(title="Students per performance band", ylabel="Students")
    return _save(fig, out_dir, "performance_bands.png")


def parent_education_heatmap(df, out_dir: Path) -> Path:
    means = group_means(df, "ParentEduc")
    order = [level for level in PARENT_EDUC_LEVELS if level in means.index]
    means = means.loc[order + [i for i in means.index if i not in order]]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.heatmap(means, annot=True, fmt=".1f", cmap="Blues", ax=ax)
    ax.set(title="Mean score by parent education", xlabel="", ylabel="")
    return _save(fig, out_dir, "parent_education_heatmap.png")


def study_hours_scatter(df, out_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(df["StudyHours"], df["AverageScore"], s=10, alpha=0.4, color=BLUE)
    fit = fit_linear_regression(df, ["StudyHours"])
    xs = np.linspace(df["StudyHours"].min(), df["StudyHours"].max(), 50)
    ax.plot(
        xs,
        fit["intercept"] + fit["coefficients"]["StudyHours"] * xs,
        color=ORANGE,
        label=f"Linear fit (R2 = {fit['r2']:.2f})",
    )
    ax.set(
        title="Weekly study hours vs average score",
        xlabel="Study hours per week",
        ylabel="Average score",
    )
    ax.legend()
    return _save(fig, out_dir, "study_hours_vs_score.png")


def attendance_boxplot(df, out_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(
        data=df, x="AttendanceBand", y="AverageScore", order=ATTENDANCE_LABELS, color=BLUE, ax=ax
    )
    ax.set(
        title="Average score by attendance band",
        xlabel="Attendance band (<75, 75-89, 90+)",
        ylabel="Average score",
    )
    return _save(fig, out_dir, "attendance_boxplot.png")


def at_risk_outcomes(df, out_dir: Path) -> Path:
    flagged = flag_at_risk(df)
    rates = {
        "Not at risk": 1 - df.loc[~flagged, "Passed"].mean() if (~flagged).any() else 0,
        "At risk": 1 - df.loc[flagged, "Passed"].mean() if flagged.any() else 0,
    }
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(list(rates), [v * 100 for v in rates.values()], color=[BLUE, ORANGE])
    ax.bar_label(ax.containers[0], fmt="%.1f%%")
    ax.set(title="Fail rate by at-risk flag", ylabel="Students failing (%)")
    return _save(fig, out_dir, "at_risk_fail_rate.png")


ALL_CHARTS = [
    score_distribution,
    performance_bands,
    parent_education_heatmap,
    study_hours_scatter,
    attendance_boxplot,
    at_risk_outcomes,
]


def save_all(df, out_dir: str | Path) -> list[Path]:
    out_dir = Path(out_dir)
    return [chart(df, out_dir) for chart in ALL_CHARTS]
