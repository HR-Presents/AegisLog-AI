# Testing

Run the complete local checks with:

```bash
pip install -e '.[dev]'
ruff check .
pytest -q
```

CI repeats linting and tests on supported Python versions. Additional workflows build the distribution package and audit installed dependencies.

Fixtures must be synthetic/sanitized. Security-rule tests should include both expected matches and, as the rule set matures, benign near-matches to reduce false positives.
