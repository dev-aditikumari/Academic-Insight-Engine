PY = .venv/bin/python

.PHONY: setup test lint data report

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check .

data:
	$(PY) -m academic_insight generate

report: data
	$(PY) -m academic_insight report --input data/synthetic_students.csv --out-dir output
