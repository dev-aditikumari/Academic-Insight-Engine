"""Seeded generator for a SYNTHETIC student performance dataset.

The original notebook used a spreadsheet that is not part of this repository.
Nothing produced here is real student data. The relationships (more study
hours and better attendance give higher scores) are assumptions written into
the generator, so any "finding" on this data only reflects those assumptions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .schema import (
    GENDERS,
    MARITAL_STATUSES,
    PARENT_EDUC_LEVELS,
    STUDY_HOUR_LABELS,
)

DEFAULT_FILENAME = "synthetic_students.csv"


def study_hour_label(hours: float) -> str:
    if hours < 5:
        return STUDY_HOUR_LABELS[0]
    if hours <= 10:
        return STUDY_HOUR_LABELS[1]
    return STUDY_HOUR_LABELS[2]


def generate_students(n: int = 1000, seed: int = 42, missing_rate: float = 0.0) -> pd.DataFrame:
    """Return `n` synthetic students.

    `missing_rate` blanks that share of ParentEduc values, which is useful for
    exercising the cleaning step. It is 0 by default.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= missing_rate < 1:
        raise ValueError("missing_rate must be in [0, 1)")

    rng = np.random.default_rng(seed)
    ability = rng.normal(0, 1, n)

    gender = rng.choice(GENDERS, n, p=[0.51, 0.49])
    parent_educ_idx = rng.choice(len(PARENT_EDUC_LEVELS), n, p=[0.12, 0.2, 0.22, 0.2, 0.18, 0.08])
    marital = rng.choice(MARITAL_STATUSES, n, p=[0.55, 0.2, 0.2, 0.05])

    study_hours = np.clip(rng.gamma(4.0, 1.9, n) + 1.0 * ability, 0, 40)
    attendance = np.clip(rng.normal(86, 9, n) + 2.0 * ability, 40, 100)
    parental_support = np.clip(
        np.rint(2.5 + 0.25 * parent_educ_idx + rng.normal(0, 1, n)), 1, 5
    ).astype(int)
    previous_grade = np.clip(66 + 9 * ability + rng.normal(0, 5, n), 0, 100)

    base = (
        3
        + 0.45 * previous_grade
        + 1.1 * study_hours
        + 0.22 * attendance
        + 1.0 * parent_educ_idx
        + 0.8 * parental_support
    )

    def score(subject_shift: float, noise_sd: float) -> np.ndarray:
        values = base + subject_shift + rng.normal(0, noise_sd, n)
        return np.clip(np.rint(values), 0, 100).astype(int)

    math = score(-2.0, 8.0)
    reading = score(1.0 + 3.0 * (gender == "female"), 7.0)
    writing = score(2.0 + 4.0 * (gender == "female"), 7.0)

    df = pd.DataFrame(
        {
            "StudentID": np.arange(1, n + 1),
            "Gender": gender,
            "ParentEduc": [PARENT_EDUC_LEVELS[i] for i in parent_educ_idx],
            "ParentMaritalStatus": marital,
            "WklyStudyHours": [study_hour_label(h) for h in study_hours],
            "StudyHours": np.round(study_hours, 1),
            "AttendanceRate": np.round(attendance, 1),
            "PreviousGrade": np.round(previous_grade, 1),
            "ParentalSupport": parental_support,
            "MathScore": math,
            "ReadingScore": reading,
            "WritingScore": writing,
        }
    )

    if missing_rate > 0:
        mask = rng.random(n) < missing_rate
        df["ParentEduc"] = df["ParentEduc"].astype(object).mask(mask, None)
    return df
