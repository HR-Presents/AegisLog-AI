# Contributing

Use Python 3.10+ and keep changes defensive, testable, and local-first.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check .
```

New detections should include tests and should avoid overstating certainty. Prefer evidence-backed labels such as "possible" or "suspicious" when a pattern is not conclusive. Never add real credentials or production logs to fixtures.
