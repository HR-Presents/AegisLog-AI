# Changelog

## 1.5.0 - 2026-09-02

- Improved incident and investigation terminal workflows with ordered, incident-specific analyst next actions and clearer evidence-led guidance.
- Added runtime-aware command examples so standalone Windows builds show `AegisLog.exe` while source installs continue to show `aegislog`.
- Unified operator startup/status presentation across single-file, multi-source, and native live monitoring while preserving immediate initial-result rendering.
- Hardened long-running live trend state with ingest-cycle aggregation, bounded history, and count-preserving compaction under unusually high event rates.
- Added stress regressions for large batches and bounded rolling live/multi-source windows plus a dedicated live-state benchmark.
- Preserved the defensive, local-first, read-only security model; findings and ATT&CK mappings remain investigative signals rather than proof or attribution.
- Prepared version-locked v1.5.0 package, customer-bundle, release-note, checksum, and immutable release workflow metadata.

## 1.4.2 - 2026-08-30

- Fixed interactive control-center launch paths for the real-time file dashboard, multi-source live SOC, native analysis, and native real-time monitor.
- Added menu-level exception containment so launch failures are reported inside AegisLog instead of unexpectedly closing the control center.
- Added regression coverage for interactive launch defaults and crash containment.
- Retained the v1.4.1 live-monitoring improvements, Windows telemetry normalization, Security Event intelligence, incident IDs, MITRE context, watch profiles, native collectors, and local-first/read-only analysis.
- Published the Windows single-file `AegisLog.exe` with a SHA-256 checksum.

## 1.4.1 - 2026-08-30

- Clarified live-monitor startup behavior: by default AegisLog follows newly appended lines, with `--from-start` available when existing file content should also be processed.
- Reworked live-rate and activity wording to distinguish average rate, rolling activity, waiting state, and time since last activity.
- Deduplicated growing versions of the same live finding, including repeated authentication-failure scenarios.
- Improved first-run live dashboard messaging and added regression coverage based on real Windows testing.

## 1.4.0 - 2026-08-29

- Improved Windows Event Log timestamp, provider, level, and service normalization.
- Added friendly permission guidance for protected Windows Security Event Log access while keeping normal operation unprivileged.
- Improved Docker readiness checks to distinguish missing CLI, unavailable engine/access, and ready state.
- Surfaced actionable `INC-XXXXXXXX` incident IDs and aligned dashboard guidance with `incidents`, `investigate`, and `explain` workflows.
- Added defensive Windows Security Event context for selected audit events, including failed logons, privileged logons, process creation, account changes, group membership changes, lockouts, and audit-log clearing.
- Added regression coverage based on real Windows acceptance-test findings.
- Published the Windows single-file executable and checksum while preserving the local-first, read-only defensive model.

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
- Added a conventional, script-friendly `aegislog --version` terminal option.

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
