# Output conventions

Severity order is `INFO < LOW < MEDIUM < HIGH < CRITICAL`. V0.2 rules currently emit MEDIUM, HIGH, and CRITICAL findings.

Finding titles describe the detected pattern, evidence contains a sanitized/redacted excerpt or correlation summary, and recommendations suggest investigation rather than automatic action. Machine-readable JSON mirrors these concepts and adds anomaly and incident objects.
