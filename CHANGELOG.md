# Changelog

## 1.0.0 - Release candidate

- Promoted the complete terminal analysis, SOC workflow, persistent entity graph,
  streaming, behavioral correlation, collectors, reports, and optional AI stack.
- Added versioned, allowlisted, atomic configuration with private file permissions.
- Hardened collector execution with an executable allowlist and argument isolation.
- Replaced legacy incident identifiers with deterministic SHA-256 identifiers.
- Removed dynamic SQL composition and expanded static application security checks.
- Bounded remote AI response bodies and rejected non-object JSON responses.
- Escaped log-derived and database-derived terminal table values.
- Expanded CI to Python 3.10–3.13 and added Bandit, Twine, and release checksums.

## 0.9.0 - Release candidate hardening

- Completed the security, configuration migration, packaging, and terminal-safety gate.

## 0.2.0 - Unreleased

- Added generic, syslog, journald/JSON, and web access-log parsing.
- Added `watch` for live appended-log analysis.
- Added `anomalies` with local frequency-based scoring.
- Added `ask` with a local investigation summary and privacy-first provider abstraction.
- Added `incidents` to correlate findings by investigation category.
- Added non-secret local configuration.
- Extended JSON reports with anomalies and incidents.
- Added Linux/macOS and Windows installation helpers.
- Added security guidance, dependency audit workflow, demo guide, and broader tests.

## 0.1.0

- Initial installable terminal CLI.
- Deterministic defensive detection rules, redaction, scanning, threat view, and JSON reporting.
