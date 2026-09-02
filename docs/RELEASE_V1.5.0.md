# AegisLog AI v1.5.0

AegisLog AI v1.5.0 is a terminal analyst-workflow, live-monitoring, and long-running stability release built on the v1.4.x production line.

## Analyst workflow

- Incident and investigation views now provide clearer, ordered next actions for investigation, explanation, evidence saving, entity intelligence, and MITRE context.
- Frozen Windows builds surface commands using `AegisLog.exe`, while source installs continue to use `aegislog`.
- Paths containing spaces are displayed safely with quoting in suggested analyst commands.
- Terminal output uses the shared semantic theme for incident IDs, severity, confidence, evidence, entities, and ATT&CK context.
- Guidance explicitly keeps findings evidence-led: signals are not proof of compromise or attribution.

## Live monitoring

- Single-file, multi-source, and native live modes now use a consistent operator startup view.
- Startup context makes the active profile, monitoring mode, rolling window, refresh behavior, sources, and collector context easier to understand.
- Initial analyzed results remain visible immediately before continuous refresh, preserving the v1.4.6 Windows terminal fix.
- Read-only monitoring and safe Ctrl+C stop behavior are communicated more clearly.

## Performance and stability

- Trend signal history is aggregated per ingest cycle rather than retaining one history entry per input line.
- Trend history has a hard bounded bucket ceiling for unusually high-frequency workloads.
- Aggregate failed-login, error, and firewall-block counts are preserved when old adjacent buckets must be compacted.
- Added stress-style regression coverage for large batches and bounded live/multi-source rolling windows.
- Added a dedicated live-state benchmark and refreshed performance documentation.

## Quality

- v1.5 development was validated continuously through CI, security checks, package builds, and Windows single-executable builds.
- Release metadata, package artifacts, customer bundle names, and the immutable release workflow are version-locked to v1.5.0.
- The release workflow refuses to reuse an existing v1.5.0 tag or release and requires explicit main-branch confirmation before publication.

## Customer delivery

The primary Windows release remains a single `AegisLog.exe` console executable. No Python installation or virtual environment is required for the released EXE.

A matching `AegisLog.exe.sha256` checksum is published beside the executable.

## Security model

AegisLog remains defensive, local-first, and read-only. Findings, anomalies, correlations, and ATT&CK mappings are investigative signals rather than proof of compromise or attribution. The application does not automatically change accounts, firewall rules, services, or system configuration.

## Windows note

The executable is currently unsigned. Windows SmartScreen or antivirus products may show reputation-based warnings even when the published SHA-256 checksum matches.
