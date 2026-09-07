# AegisLog AI v1.6.0

AegisLog AI v1.6.0 improves analyst workflow quality, native telemetry diagnostics, live-source resilience, and long-running multi-source runtime bounds while preserving the project's local-first, read-only defensive model.

## Highlights

- Added an analyst triage summary to investigations using existing severity and confidence signals, with explicit non-attribution guidance.
- Improved Windows Event Log, journald, and Docker diagnostics by distinguishing unsupported sources from temporarily unavailable sources and providing source-specific read-only troubleshooting guidance.
- Hardened single-file and multi-source live monitoring so temporary source loss is reported clearly, the current dashboard stays visible, recovery is recognized, and monitoring resumes safely.
- Improved long-running multi-source memory behavior by aggregating arrival history, bounding arrival buckets, and bounding alert fingerprint state.
- Added focused regression coverage for investigation triage, native diagnostics, source loss/recovery, 50,000-line ingest batches, bounded runtime state, and configuration validation.
- Preserved deterministic local analysis as the primary workflow. Findings, anomaly scores, incident priorities, and ATT&CK mappings are investigative signals and are not proof of compromise, attribution, or attacker intent.

## Distribution

The GitHub release publishes the standalone Windows `AegisLog.exe` plus `AegisLog.exe.sha256`. The executable does not require a separate Python installation or virtual environment for normal customer use.

The executable is currently unsigned. Windows SmartScreen or endpoint-security reputation warnings may therefore appear even when the published checksum matches.

## Safety model

AegisLog remains defensive and read-only. It does not automatically remediate hosts, modify source telemetry, change host security policy, deploy persistence, steal credentials, evade security controls, or provide exploitation tooling.

## Verification

Verify the downloaded executable against the accompanying SHA-256 file before use. The release workflow also refuses to overwrite or reuse an existing `v1.6.0` tag or GitHub release.
