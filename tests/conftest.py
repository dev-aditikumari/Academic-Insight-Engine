import pandas as pd
import pytest

from academic_insight.synthetic import generate_students


@pytest.fixture(scope="session")
def synthetic_df():
    return generate_students(n=300, seed=7)


@pytest.fixture
def tiny_df():
    return pd.DataFrame(
        {
            "Gender": ["female", "male", "female", "male"],
            "ParentEduc": ["high school", "high school", "bachelor's degree", "bachelor's degree"],
            "ParentMaritalStatus": ["married", "single", "married", "single"],
            "WklyStudyHours": ["<5", "5-10", "5-10", ">10"],
            "StudyHours": [2.0, 6.0, 8.0, 12.0],
            "AttendanceRate": [60.0, 80.0, 90.0, 100.0],
            "PreviousGrade": [40.0, 60.0, 70.0, 90.0],
            "ParentalSupport": [1, 2, 4, 5],
            "MathScore": [30, 50, 70, 90],
            "ReadingScore": [40, 60, 80, 100],
            "WritingScore": [50, 70, 90, 100],
        }
    )
