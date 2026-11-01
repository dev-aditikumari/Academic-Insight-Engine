import pandas as pd
import pytest

from academic_insight.features import add_features


def frame(score, attendance=80.0):
    return pd.DataFrame(
        {
            "MathScore": [score],
            "ReadingScore": [score],
            "WritingScore": [score],
            "AttendanceRate": [attendance],
        }
    )


def test_average_score(tiny_df):
    out = add_features(tiny_df)
    assert out["AverageScore"].tolist() == pytest.approx([40.0, 60.0, 80.0, 96.6666667])


@pytest.mark.parametrize(
    "score,passed,band",
    [
        (49.9, False, "Fail"),
        (50, True, "Satisfactory"),
        (64.9, True, "Satisfactory"),
        (65, True, "Good"),
        (79.9, True, "Good"),
        (80, True, "Excellent"),
        (100, True, "Excellent"),
    ],
)
def test_pass_flag_and_band_boundaries(score, passed, band):
    out = add_features(frame(score))
    assert bool(out.loc[0, "Passed"]) is passed
    assert out.loc[0, "PerformanceBand"] == band


@pytest.mark.parametrize(
    "attendance,band",
    [(0, "Low"), (74.9, "Low"), (75, "Medium"), (89.9, "Medium"), (90, "High"), (100, "High")],
)
def test_attendance_band_boundaries(attendance, band):
    assert add_features(frame(60, attendance)).loc[0, "AttendanceBand"] == band


def test_original_columns_untouched(tiny_df):
    out = add_features(tiny_df)
    pd.testing.assert_frame_equal(out[tiny_df.columns], tiny_df)
