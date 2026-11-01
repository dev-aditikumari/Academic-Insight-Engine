import pandas as pd
import pytest

from academic_insight.cli import main


def test_generate_writes_csv(tmp_path):
    out = tmp_path / "synthetic_students.csv"
    assert main(["generate", "--n", "50", "--seed", "5", "--out", str(out)]) == 0
    assert len(pd.read_csv(out)) == 50


def test_generate_then_report_end_to_end(tmp_path, capsys):
    data = tmp_path / "synthetic_students.csv"
    out_dir = tmp_path / "out"
    assert main(["generate", "--n", "400", "--out", str(data)]) == 0
    assert main(["report", "--input", str(data), "--out-dir", str(out_dir)]) == 0

    report = (out_dir / "report.md").read_text(encoding="utf-8")
    assert "SYNTHETIC DATA" in report
    assert "At-risk students" in report
    assert "Students: 400" in report
    charts = sorted((out_dir / "charts").glob("*.png"))
    assert len(charts) == 6
    assert all(p.stat().st_size > 1000 for p in charts)
    assert "Wrote report" in capsys.readouterr().out


def test_report_with_missing_values_still_runs(tmp_path):
    data = tmp_path / "synthetic_students.csv"
    main(["generate", "--n", "300", "--missing-rate", "0.1", "--out", str(data)])
    assert main(["report", "--input", str(data), "--out-dir", str(tmp_path / "o")]) == 0


def test_report_on_missing_file_returns_error(tmp_path, capsys):
    assert main(["report", "--input", str(tmp_path / "nope.csv"), "--out-dir", str(tmp_path)]) == 1
    assert "not found" in capsys.readouterr().err


def test_report_on_bad_schema_returns_error(tmp_path, capsys):
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"x": [1]}).to_csv(bad, index=False)
    assert main(["report", "--input", str(bad), "--out-dir", str(tmp_path)]) == 1
    assert "missing columns" in capsys.readouterr().err


def test_real_named_file_is_not_labelled_synthetic(tmp_path):
    data = tmp_path / "synthetic_students.csv"
    main(["generate", "--n", "100", "--out", str(data)])
    renamed = tmp_path / "exam_results.csv"
    data.rename(renamed)
    main(["report", "--input", str(renamed), "--out-dir", str(tmp_path / "o")])
    assert "SYNTHETIC DATA" not in (tmp_path / "o" / "report.md").read_text(encoding="utf-8")


def test_command_required():
    with pytest.raises(SystemExit):
        main([])
