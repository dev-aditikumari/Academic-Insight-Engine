"""Column names and allowed values shared across the package."""

SCORE_COLUMNS = ["MathScore", "ReadingScore", "WritingScore"]

NUMERIC_RANGES = {
    "MathScore": (0, 100),
    "ReadingScore": (0, 100),
    "WritingScore": (0, 100),
    "StudyHours": (0, 40),
    "AttendanceRate": (0, 100),
    "PreviousGrade": (0, 100),
    "ParentalSupport": (1, 5),
}

CATEGORICAL_COLUMNS = ["Gender", "ParentEduc", "ParentMaritalStatus", "WklyStudyHours"]

REQUIRED_COLUMNS = CATEGORICAL_COLUMNS + list(NUMERIC_RANGES)

GENDERS = ["female", "male"]
PARENT_EDUC_LEVELS = [
    "some high school",
    "high school",
    "some college",
    "associate's degree",
    "bachelor's degree",
    "master's degree",
]
MARITAL_STATUSES = ["married", "single", "divorced", "widowed"]
STUDY_HOUR_LABELS = ["<5", "5-10", ">10"]
