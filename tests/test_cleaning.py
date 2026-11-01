import pandas as pd
import pytest

from academic_insight.cleaning import clean_students, normalise_hour_label


@pytest.mark.parametrize(
    "raw,expected", [("5 - 10", "5-10"), ("< 5", "<5"), (" > 10 ", ">10"), ("5-10", "5-10")]
)
def test_normalise_hour_label(raw, expected):
    assert normalise_hour_label(raw) == expected


def test_drops_unnamed_index_column(tiny_df):
    tiny_df.insert(0, "Unnamed: 0", range(len(tiny_df)))
    assert "Unnamed: 0" not in clean_students(tiny_df).columns


def test_removes_duplicates(tiny_df):
    doubled = pd.concat([tiny_df, tiny_df.iloc[[0]]], ignore_index=True)
    assert len(clean_students(doubled)) == len(tiny_df)


def test_labels_and_whitespace_normalised(tiny_df):
    tiny_df.loc[1, "WklyStudyHours"] = "5 - 10"
    tiny_df.loc[0, "Gender"] = " female "
    out = clean_students(tiny_df)
    assert out.loc[1, "WklyStudyHours"] == "5-10"
    assert out.loc[0, "Gender"] == "female"


def test_missing_category_becomes_unknown(tiny_df):
    tiny_df.loc[2, "ParentEduc"] = None
    assert clean_students(tiny_df).loc[2, "ParentEduc"] == "unknown"


def test_rows_without_scores_are_dropped(tiny_df):
    tiny_df.loc[3, "ReadingScore"] = None
    out = clean_students(tiny_df)
    assert len(out) == 3


def test_missing_predictor_filled_with_median(tiny_df):
    tiny_df.loc[0, "StudyHours"] = None
    out = clean_students(tiny_df)
    assert out.loc[0, "StudyHours"] == 8.0  # median of 6, 8, 12


def test_input_is_not_modified(tiny_df):
    before = tiny_df.copy()
    clean_students(tiny_df)
    pd.testing.assert_frame_equal(tiny_df, before)
