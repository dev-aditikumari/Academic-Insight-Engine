"""Command line interface: `python -m academic_insight generate|report`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .loading import SchemaError
from .report import run_report
from .synthetic import DEFAULT_FILENAME, generate_students


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="academic_insight", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="write a SYNTHETIC student dataset to CSV")
    gen.add_argument("--n", type=int, default=1000, help="number of students")
    gen.add_argument("--seed", type=int, default=42)
    gen.add_argument(
        "--missing-rate", type=float, default=0.0, help="share of ParentEduc values to blank out"
    )
    gen.add_argument("--out", type=Path, default=Path("data") / DEFAULT_FILENAME)

    rep = sub.add_parser("report", help="analyse a dataset and write a markdown report")
    rep.add_argument("--input", type=Path, required=True, help="CSV or Excel file")
    rep.add_argument("--out-dir", type=Path, default=Path("output"))
    rep.add_argument("--report-name", default="report.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "generate":
            df = generate_students(args.n, args.seed, args.missing_rate)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(args.out, index=False)
            print(f"Wrote {len(df)} SYNTHETIC students to {args.out}")
        else:
            path = run_report(args.input, args.out_dir, args.report_name)
            print(f"Wrote report to {path}")
    except (SchemaError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0
