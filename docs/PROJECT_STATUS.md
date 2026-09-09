# Project status

AegisLog is a released, terminal-first defensive security platform. The current published stable release is **v1.6.0**.

The `main` branch contains reviewed improvements newer than that stable release, including the latest terminal UI and public documentation polish. Those changes remain **unreleased** until an explicit release is completed.

## Current capabilities

- Local-first log analysis with deterministic defensive detections.
- Responsive terminal workflows for static analysis, live monitoring, and multi-source monitoring.
- Windows Event Log, journald, Docker, and file-based defensive collection workflows where supported.
- Incident correlation, investigation timelines, entity intelligence, MITRE ATT&CK context, anomaly scoring, evidence-led explanations, and analyst triage summaries.
- Persistent investigation/case history and bounded analysis workflows.
- Declarative JSON detection rules and structured parsing.
- Secret/privacy redaction, terminal sanitization, defensive data-handling boundaries, and read-only operation.
- Optional compatible AI providers while keeping the core workflow usable without an external AI service.
- Structured reports, baselines, behavior comparison, hunting, and indicator extraction.
- Automated CI, security checks, package builds, Windows one-file executable builds, smoke tests, and release checksums.

## Current `main` UI

Recent reviewed work on `main` improves the operator experience without changing the defensive analysis model:

- full-width Mission Control layouts with narrow-terminal fallbacks;
- consistent AegisLog workspace headers and shared page chrome;
- restrained structural colors with stronger severity emphasis;
- clearer source-input hierarchy;
- explicit analysis-completion status before investigation results;
- compact report-ready handoff messaging;
- clearer System Health and Command Reference status summaries;
- responsive system/command tables on smaller terminals.

## Windows distribution

The primary Windows release artifact is a standalone `AegisLog.exe`; Python and a virtual environment are not required for the released executable. A matching SHA-256 checksum is published with the stable release.

The published executable is unsigned, so Windows SmartScreen or antivirus reputation warnings can occur even when the published checksum matches.

GitHub Actions artifacts are build/validation outputs rather than the permanent customer distribution channel. Official customer downloads are GitHub Release assets.

## Security posture

AegisLog is defensive and read-only. Findings, anomaly scores, correlations, confidence values, incident priorities, and ATT&CK mappings are investigative signals rather than proof of compromise or attribution.

The application does not automatically modify accounts, firewall rules, services, telemetry sources, or host configuration, and remote AI is not required for the core workflow.

## Release status

- **Published stable:** v1.6.0
- **Current newer work on `main`:** unreleased

See [`RELEASE_V1.6.0.md`](RELEASE_V1.6.0.md), [`RELEASE_V1.6.1.md`](RELEASE_V1.6.1.md), [`ROADMAP.md`](ROADMAP.md), and the repository [`CHANGELOG.md`](../CHANGELOG.md) for details.
