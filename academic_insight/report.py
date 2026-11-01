"""Build the markdown report and charts for a dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import analysis, charts, features
from .cleaning import clean_students
from .features import add_features
from .loading import load_students


def _table(df: pd.DataFrame, floatfmt: str = "{:.2f}") -> str:
    df = df.reset_index().rename(columns={"index": "Item"})
    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    rule = "|" + "|".join("---" for _ in df.columns) + "|"
    rows = [
        "| "
        + " | ".join(floatfmt.format(v) if isinstance(v, float) else str(v) for v in row)
        + " |"
        for row in df.itertuples(index=False)
    ]
    return "\n".join([header, rule, *rows])


def build_report(df: pd.DataFrame, source: str, chart_paths: list[Path], synthetic: bool) -> str:
    desc = analysis.describe_scores(df)
    corr = analysis.score_correlations(df).rename("pearson_r").to_frame()
    reg = analysis.fit_linear_regression(df)
    risk = analysis.at_risk_summary(df)
    gender = analysis.group_means(df, "Gender")
    educ = analysis.group_means(df, "ParentEduc")
    marital = analysis.group_means(df, "ParentMaritalStatus")
    pass_by_band = analysis.pass_rate_by(df, "AttendanceBand").rename("pass_rate").to_frame()
    coef = pd.DataFrame(
        {"coefficient": reg["coefficients"].values()}, index=list(reg["coefficients"])
    )

    lines = ["# Academic Insight report", ""]
    if synthetic:
        lines += [
            "> SYNTHETIC DATA. The numbers below come from a seeded generator, not from real "
            "students. They show the pipeline working, not facts about any school.",
            "",
        ]
    lines += [
        f"Source file: `{source}`  ",
        f"Students: {len(df)}",
        "",
        "## Score summary",
        "",
        _table(desc),
        "",
        f"Pass mark: average score of {features.PASS_MARK:.0f} or more. "
        f"Passed: {int(df['Passed'].sum())} of {len(df)} ({df['Passed'].mean():.1%}).",
        "",
        "## Correlation with average score",
        "",
        _table(corr, "{:.3f}"),
        "",
        "## Linear regression on average score",
        "",
        f"Intercept {reg['intercept']:.2f}, R2 {reg['r2']:.3f}.",
        "",
        _table(coef, "{:.3f}"),
        "",
        "## Group comparisons (mean scores)",
        "",
        "By gender:",
        "",
        _table(gender),
        "",
        "By parent education:",
        "",
        _table(educ),
        "",
        "By parent marital status:",
        "",
        _table(marital),
        "",
        "Pass rate by attendance band:",
        "",
        _table(pass_by_band, "{:.3f}"),
        "",
        "## At-risk students",
        "",
        f"A student is flagged when at least {analysis.MIN_SIGNALS} of these hold: "
        f"attendance below "
        f"{analysis.ATTENDANCE_THRESHOLD:.0f}%, study hours below "
        f"{analysis.STUDY_HOURS_THRESHOLD:.0f} per week, previous grade below "
        f"{analysis.PREVIOUS_GRADE_THRESHOLD:.0f}.",
        "",
        f"Flagged: {risk['at_risk']} of {risk['students']} ({risk['at_risk_share']:.1%}). "
        f"Fail rate among flagged: {risk['fail_rate_at_risk']:.1%}; "
        f"among the rest: {risk['fail_rate_not_at_risk']:.1%}.",
        "",
        "## Charts",
        "",
    ]
    for path in chart_paths:
        lines += [f"![{path.stem}](charts/{path.name})", ""]
    return "\n".join(lines)


def run_report(
    input_path: str | Path,
    out_dir: str | Path,
    report_name: str = "report.md",
    synthetic: bool | None = None,
) -> Path:
    """Load, clean, analyse and write report plus charts. Returns the report path."""
    input_path = Path(input_path)
    out_dir = Path(out_dir)
    if synthetic is None:
        synthetic = "synthetic" in input_path.name.lower()

    df = add_features(clean_students(load_students(input_path)))
    chart_paths = charts.save_all(df, out_dir / "charts")
    text = build_report(df, input_path.name, chart_paths, synthetic)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / report_name
    report_path.write_text(text + "\n", encoding="utf-8")
    return report_path
