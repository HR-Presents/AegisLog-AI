# Project status

AegisLog AI is a released, terminal-first defensive security platform. The current stable release is **v1.6.0**.

## Current stable capabilities

- Local-first log analysis with deterministic defensive detections.
- Rich terminal dashboards for file analysis, live monitoring, and multi-source monitoring.
- Windows Event Log, journald, Docker, and file-based defensive collection workflows where supported.
- Incident correlation, investigation timelines, entity intelligence, MITRE ATT&CK context, anomaly scoring, evidence-led explanations, and analyst triage summaries.
- Persistent investigation/case history and bounded analysis workflows.
- Declarative JSON detection rules and structured parsing.
- Secret/privacy redaction, terminal sanitization, defensive data-handling boundaries, and read-only operation.
- Optional compatible AI providers while keeping the core workflow usable without an external AI service.
- JSON/HTML/Markdown-style reporting workflows, baselines, behavior comparison, hunting, and indicator extraction.
- Automated CI, security checks, package builds, Windows one-file executable builds, smoke tests, and release checksums.

## v1.6.0 reliability and operator improvements

- Investigation output now includes a conservative analyst triage summary built from existing local evidence, severity, confidence, timeline, and entity context.
- Native telemetry diagnostics distinguish unsupported sources from temporarily unavailable Windows Event Log, journald, and Docker sources and provide read-only troubleshooting guidance.
- Single-file and multi-source live monitoring report temporary source loss, keep the current dashboard visible, detect recovery, and resume through the safe cursor path.
- Long-running multi-source state now uses bounded arrival-history buckets and bounded alert-fingerprint history to avoid unbounded growth under sustained input.
- Regression coverage includes source loss/recovery, 50,000-line ingest batches, hard runtime bounds, and release metadata consistency.

## Windows distribution

The primary Windows release artifact is a standalone `AegisLog.exe`; Python and a virtual environment are not required for the released executable. A matching SHA-256 checksum is published with the release.

The executable is currently unsigned. Windows SmartScreen or antivirus reputation warnings can therefore occur even when the published checksum matches.

## Security posture

AegisLog is defensive and read-only. Findings, anomaly scores, correlations, confidence values, incident priorities, and ATT&CK mappings are investigative signals rather than proof of compromise or attribution. The application does not automatically modify accounts, firewall rules, services, telemetry sources, or host configuration.

## Current release

Stable: **v1.6.0**

See [`RELEASE_V1.6.0.md`](RELEASE_V1.6.0.md) for release-specific changes and [`ROADMAP.md`](ROADMAP.md) for future maintenance and development priorities.
