"""Read student data from CSV or Excel and validate its schema."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .schema import NUMERIC_RANGES, REQUIRED_COLUMNS


class SchemaError(ValueError):
    """Raised when a dataset does not match the expected schema."""


def read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise SchemaError(f"Unsupported file type '{suffix}'. Use .csv, .xlsx or .xls")


def validate_schema(df: pd.DataFrame) -> None:
    """Raise SchemaError listing every problem found."""
    problems: list[str] = []

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        problems.append(f"missing columns: {', '.join(missing)}")

    for column, (low, high) in NUMERIC_RANGES.items():
        if column not in df.columns:
            continue
        values = pd.to_numeric(df[column], errors="coerce")
        bad_type = int((values.isna() & df[column].notna()).sum())
        if bad_type:
            problems.append(f"column '{column}' has {bad_type} non-numeric value(s)")
            continue
        out_of_range = int(((values < low) | (values > high)).sum())
        if out_of_range:
            problems.append(
                f"column '{column}' has {out_of_range} value(s) outside [{low}, {high}]"
            )

    if df.empty:
        problems.append("dataset has no rows")

    if problems:
        raise SchemaError("Invalid dataset: " + "; ".join(problems))


def load_students(path: str | Path) -> pd.DataFrame:
    df = read_table(path)
    validate_schema(df)
    return df
