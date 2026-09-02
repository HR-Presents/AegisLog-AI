# AegisLog AI v1.4.3

AegisLog AI v1.4.3 is a terminal UX and release-maintenance update built on the stable v1.4.2 line.

## Added

- Added a shared professional terminal color system across the main interactive and monitoring surfaces.
- Added consistent semantic colors for clear, review, warning, high, critical, incident, anomaly, and neutral states.
- Added theme regression tests to preserve severity and risk color semantics.

## Improved

- Updated the static analysis dashboard with clearer risk, severity, incident, anomaly, metric, and next-step styling.
- Updated the real-time file dashboard with consistent live-state, rate-spike, incident, anomaly, and risk styling.
- Updated the interactive control center, multi-source SOC dashboard, native source views, native live messages, and trend intelligence tables to use one coherent visual language.
- Preserved visible text labels so status meaning does not depend on color alone.
- Continued rendering untrusted log-derived, user-derived, and exception values as literal terminal text where appropriate.

## Maintenance

- Removed obsolete historical version-specific release workflows while retaining their release notes as project history.
- Closed the superseded V1.1 dashboard pull request rather than merging stale code into the current release line.

## Customer delivery

The Windows release remains a single `AegisLog.exe` console executable. No Python installation or virtual environment is required for the released EXE.

A matching `AegisLog.exe.sha256` checksum is published beside the executable.

## Security model

AegisLog remains defensive, local-first, and read-only. Detection signals are investigative evidence rather than proof of compromise. The application does not automatically change accounts, firewall rules, services, or system configuration.

## Windows note

The executable is currently unsigned. Windows SmartScreen or antivirus products may therefore show reputation-based warnings even when the published SHA-256 checksum matches.
