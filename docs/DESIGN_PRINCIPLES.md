# Design principles

1. Terminal first: useful without a browser or dashboard.
2. Local first: core analysis works without an AI service.
3. Evidence before explanation: deterministic observations feed AI, not the reverse.
4. Privacy by default: minimize and redact before any future remote processing.
5. No autonomous remediation: recommend; do not silently change systems.
6. Explainable severity: findings should have a clear reason and evidence.
7. Safe failure: malformed/unreadable logs should not crash an entire scan.
8. Extensible formats: normalize different log sources into a common event model.
