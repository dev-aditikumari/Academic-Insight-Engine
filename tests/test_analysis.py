import numpy as np
import pandas as pd
import pytest

from academic_insight import analysis
from academic_insight.features import add_features


def risk_frame(attendance, hours, grade):
    return pd.DataFrame(
        {"AttendanceRate": [attendance], "StudyHours": [hours], "PreviousGrade": [grade]}
    )


def test_correlation_sign_positive(tiny_df):
    df = add_features(tiny_df)
    corr = analysis.score_correlations(df)
    assert (corr > 0.9).all()


def test_correlation_sign_negative(tiny_df):
    df = add_features(tiny_df)
    df["StudyHours"] = -df["AverageScore"]
    assert analysis.score_correlations(df, ["StudyHours"])["StudyHours"] == pytest.approx(-1.0)


def test_correlations_sorted_by_strength(tiny_df):
    df = add_features(tiny_df)
    df["ParentalSupport"] = [3, 1, 4, 1]
    corr = analysis.score_correlations(df)
    assert list(corr.abs()) == sorted(corr.abs(), reverse=True)
    assert corr.index[-1] == "ParentalSupport"


def test_group_means_known_answer(tiny_df):
    means = analysis.group_means(tiny_df, "ParentEduc")
    assert means.loc["high school", "MathScore"] == 40
    assert means.loc["bachelor's degree", "WritingScore"] == 95


def test_pass_rate_by(tiny_df):
    df = add_features(tiny_df)
    rates = analysis.pass_rate_by(df, "Gender")
    assert rates["female"] == 0.5  # female averages are 40 and 80
    assert rates["male"] == 1.0


def test_describe_scores_has_average(tiny_df):
    desc = analysis.describe_scores(add_features(tiny_df))
    assert desc.loc["MathScore", "mean"] == 60
    assert "AverageScore" in desc.index


@pytest.mark.parametrize(
    "attendance,hours,grade,expected",
    [
        (80, 8, 70, False),  # no signals
        (74.9, 8, 70, False),  # one signal
        (74.9, 4.9, 70, True),  # two signals
        (75, 4.9, 70, False),  # attendance exactly on threshold is not a signal
        (80, 5, 59.9, False),  # study hours exactly on threshold is not a signal
        (80, 4.9, 59.9, True),
        (75, 5, 60, False),  # all values on thresholds
        (50, 1, 10, True),  # all three signals
    ],
)
def test_at_risk_rule_boundaries(attendance, hours, grade, expected):
    assert bool(analysis.flag_at_risk(risk_frame(attendance, hours, grade)).iloc[0]) is expected


def test_at_risk_summary_known_answer():
    df = pd.DataFrame(
        {
            "AttendanceRate": [50, 50, 90, 90],
            "StudyHours": [1, 1, 10, 10],
            "PreviousGrade": [40, 80, 80, 80],
            "Passed": [False, True, True, True],
        }
    )
    summary = analysis.at_risk_summary(df)
    assert summary["at_risk"] == 2
    assert summary["at_risk_share"] == 0.5
    assert summary["fail_rate_at_risk"] == 0.5
    assert summary["fail_rate_not_at_risk"] == 0.0


def test_regression_recovers_known_coefficients():
    rng = np.random.default_rng(0)
    x1 = rng.uniform(0, 10, 200)
    x2 = rng.uniform(0, 10, 200)
    df = pd.DataFrame({"a": x1, "b": x2, "y": 5 + 2 * x1 - 3 * x2})
    fit = analysis.fit_linear_regression(df, ["a", "b"], "y")
    assert fit["intercept"] == pytest.approx(5)
    assert fit["coefficients"]["a"] == pytest.approx(2)
    assert fit["coefficients"]["b"] == pytest.approx(-3)
    assert fit["r2"] == pytest.approx(1.0)


def test_regression_r2_below_one_with_noise(synthetic_df):
    fit = analysis.fit_linear_regression(add_features(synthetic_df))
    assert 0.3 < fit["r2"] < 1.0
    assert fit["coefficients"]["StudyHours"] > 0
