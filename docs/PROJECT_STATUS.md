# Project status

AegisLog AI is a released, terminal-first defensive security platform. The current stable release is **v1.4.6**.

## Current stable capabilities

- Local-first log analysis with deterministic defensive detections.
- Rich terminal dashboards for file analysis, live monitoring, and multi-source monitoring.
- Windows Event Log, journald, Docker, and file-based defensive collection workflows where supported.
- Incident correlation, investigation timelines, entity intelligence, MITRE ATT&CK context, anomaly scoring, and evidence-led explanations.
- Persistent investigation/case history and bounded analysis workflows.
- Declarative JSON detection rules and structured parsing.
- Secret/privacy redaction, terminal sanitization, defensive data-handling boundaries, and read-only operation.
- Optional compatible AI providers while keeping the core workflow usable without an external AI service.
- JSON/HTML/Markdown-style reporting workflows, baselines, behavior comparison, hunting, and indicator extraction.
- Automated CI, security checks, package builds, Windows one-file executable builds, smoke tests, and release checksums.

## Windows distribution

The primary Windows release artifact is a standalone `AegisLog.exe`; Python and a virtual environment are not required for the released executable. A matching SHA-256 checksum is published with the release.

The executable is currently unsigned. Windows SmartScreen or antivirus reputation warnings can therefore occur even when the published checksum matches.

## Security posture

AegisLog is defensive and read-only. Findings, anomaly scores, correlations, confidence values, and ATT&CK mappings are investigative signals rather than proof of compromise or attribution. The application does not automatically modify accounts, firewall rules, services, or host configuration.

## Current release

Stable: **v1.4.6**

See [`RELEASE_V1.4.6.md`](RELEASE_V1.4.6.md) for release-specific changes and [`ROADMAP.md`](ROADMAP.md) for planned work.
