import pandas as pd
import pytest

from academic_insight.schema import NUMERIC_RANGES, REQUIRED_COLUMNS
from academic_insight.synthetic import generate_students, study_hour_label


def test_same_seed_gives_same_data():
    pd.testing.assert_frame_equal(generate_students(200, seed=1), generate_students(200, seed=1))


def test_different_seed_gives_different_data():
    a = generate_students(200, seed=1)
    b = generate_students(200, seed=2)
    assert not a["MathScore"].equals(b["MathScore"])


def test_row_count_and_columns(synthetic_df):
    assert len(synthetic_df) == 300
    assert set(REQUIRED_COLUMNS) <= set(synthetic_df.columns)


@pytest.mark.parametrize("column,bounds", NUMERIC_RANGES.items())
def test_values_stay_in_range(synthetic_df, column, bounds):
    low, high = bounds
    assert synthetic_df[column].between(low, high).all()


def test_no_nulls_by_default(synthetic_df):
    assert not synthetic_df.isna().any().any()


def test_missing_rate_blanks_parent_education():
    df = generate_students(1000, seed=3, missing_rate=0.1)
    share = df["ParentEduc"].isna().mean()
    assert 0.05 < share < 0.15
    assert not df.drop(columns="ParentEduc").isna().any().any()


def test_study_hours_label_matches_numeric_hours(synthetic_df):
    expected = synthetic_df["StudyHours"].map(study_hour_label)
    # StudyHours is rounded to one decimal, so only compare rows away from a boundary
    safe = ~synthetic_df["StudyHours"].between(4.9, 5.1) & ~synthetic_df["StudyHours"].between(
        9.9, 10.1
    )
    assert (expected[safe] == synthetic_df.loc[safe, "WklyStudyHours"]).all()


@pytest.mark.parametrize(
    "hours,label", [(0, "<5"), (4.99, "<5"), (5, "5-10"), (10, "5-10"), (10.01, ">10")]
)
def test_study_hour_label_boundaries(hours, label):
    assert study_hour_label(hours) == label


@pytest.mark.parametrize(
    "kwargs", [{"n": 0}, {"n": -5}, {"missing_rate": 1.0}, {"missing_rate": -0.1}]
)
def test_invalid_arguments(kwargs):
    with pytest.raises(ValueError):
        generate_students(**kwargs)


def test_hours_and_attendance_raise_scores():
    df = generate_students(2000, seed=11)
    avg = df[["MathScore", "ReadingScore", "WritingScore"]].mean(axis=1)
    assert df["StudyHours"].corr(avg) > 0.3
    assert df["AttendanceRate"].corr(avg) > 0.1
