import pandas as pd
import pytest

from academic_insight.loading import SchemaError, load_students, read_table, validate_schema


def test_valid_frame_passes(tiny_df):
    validate_schema(tiny_df)


def test_missing_columns_are_all_listed(tiny_df):
    with pytest.raises(SchemaError) as err:
        validate_schema(tiny_df.drop(columns=["MathScore", "Gender"]))
    assert "MathScore" in str(err.value)
    assert "Gender" in str(err.value)


def test_non_numeric_values_reported(tiny_df):
    tiny_df["StudyHours"] = ["a", "b", 3, 4]
    with pytest.raises(SchemaError, match="StudyHours.*non-numeric"):
        validate_schema(tiny_df)


@pytest.mark.parametrize(
    "column,value",
    [("MathScore", 101), ("MathScore", -1), ("AttendanceRate", 100.5), ("ParentalSupport", 0)],
)
def test_out_of_range_reported(tiny_df, column, value):
    tiny_df.loc[0, column] = value
    with pytest.raises(SchemaError, match=f"{column}.*outside"):
        validate_schema(tiny_df)


def test_boundary_values_are_accepted(tiny_df):
    tiny_df.loc[0, "MathScore"] = 0
    tiny_df.loc[1, "MathScore"] = 100
    validate_schema(tiny_df)


def test_empty_frame_rejected(tiny_df):
    with pytest.raises(SchemaError, match="no rows"):
        validate_schema(tiny_df.iloc[0:0])


def test_csv_roundtrip(tiny_df, tmp_path):
    path = tmp_path / "students.csv"
    tiny_df.to_csv(path, index=False)
    pd.testing.assert_frame_equal(load_students(path), tiny_df)


def test_excel_roundtrip(tiny_df, tmp_path):
    path = tmp_path / "students.xlsx"
    tiny_df.to_excel(path, index=False)
    loaded = load_students(path)
    assert loaded["MathScore"].tolist() == tiny_df["MathScore"].tolist()


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_table(tmp_path / "nope.csv")


def test_unsupported_extension(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("x")
    with pytest.raises(SchemaError, match="Unsupported"):
        read_table(path)
