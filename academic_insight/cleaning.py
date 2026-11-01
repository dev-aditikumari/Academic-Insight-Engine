"""Cleaning steps carried over from the original notebook, made repeatable."""

from __future__ import annotations

import re

import pandas as pd

from .schema import NUMERIC_RANGES, SCORE_COLUMNS


def normalise_hour_label(label):
    """Turn '5 - 10' into '5-10' and '< 5' into '<5'."""
    if pd.isna(label):
        return label
    return re.sub(r"\s+", "", str(label))


def clean_students(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy.

    - drops leftover index columns such as 'Unnamed: 0'
    - removes exact duplicate rows
    - trims text columns and normalises weekly study hour labels
    - fills missing categorical values with 'unknown'
    - drops rows with a missing score, since scores are the target of the analysis
    - fills missing numeric predictors with the column median
    """
    out = df.copy()
    out = out.drop(columns=[c for c in out.columns if str(c).startswith("Unnamed")])
    out = out.drop_duplicates().reset_index(drop=True)

    for column in out.select_dtypes(include=["object", "string"]).columns:
        out[column] = out[column].map(lambda v: v.strip() if isinstance(v, str) else v)

    if "WklyStudyHours" in out.columns:
        out["WklyStudyHours"] = out["WklyStudyHours"].map(normalise_hour_label)

    present_scores = [c for c in SCORE_COLUMNS if c in out.columns]
    out = out.dropna(subset=present_scores).reset_index(drop=True)

    for column in out.columns:
        if column in NUMERIC_RANGES:
            if column not in SCORE_COLUMNS:
                out[column] = out[column].fillna(out[column].median())
        elif out[column].dtype == object or str(out[column].dtype) == "str":
            out[column] = out[column].fillna("unknown")
    return out
