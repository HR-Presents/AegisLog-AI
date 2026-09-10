# Project status

AegisLog is a released, terminal-first defensive security platform. The current published stable release is **v2.0.1**.

## Current capabilities

- Local-first log analysis with deterministic defensive detections.
- Responsive Mission Control workflows for static analysis, live monitoring, and multi-source monitoring.
- Windows Event Log, journald, Docker, and file-based defensive collection workflows where supported.
- Incident correlation, investigation timelines, entity intelligence, MITRE ATT&CK context, anomaly scoring, evidence-led explanations, and analyst triage summaries.
- Persistent investigation/case history and bounded analysis workflows.
- Declarative JSON detection rules and structured parsing.
- Secret/privacy redaction, terminal sanitization, defensive data-handling boundaries, and read-only operation.
- Structured reports, baselines, behavior comparison, hunting, and indicator extraction.
- Automated CI, security checks, package builds, Windows one-file executable builds, smoke tests, lock audits, checksums, and guarded release publication.

AI Analyst and remote-provider workflows are not part of the supported public v2.0 product surface.

## Current v2.0 UI

v2.0.0 rebuilt Mission Control around a clearer operator hierarchy without changing detection semantics, and v2.0.1 carries that terminal experience forward unchanged while correcting public branding and release-status surfaces:

- responsive full-width layouts with narrow-terminal fallbacks;
- balanced Investigation and Monitoring work areas on wide terminals;
- System actions separated clearly below;
- consistent AegisLog workspace headers and shared page chrome;
- version and readiness status integrated into the header hierarchy;
- the duplicate fake `SELECT >` prompt removed so the real shell prompt is authoritative;
- ASCII-safe structural chrome with explicit Windows rendering regression coverage.

## Correctness carried forward from v1.9

v2.0.1 preserves the v1.9 hardening for streaming correlation, timestamp-based authentication windows, source/account/host parsing, IPv4/IPv6 validation, out-of-order events, bounded state, and synthetic regression evaluation. The maintained synthetic corpus is regression evidence only, not an independent real-world benchmark.

## Windows distribution

The primary Windows release artifact is a standalone `AegisLog.exe`; Python and a virtual environment are not required for the released executable. A matching SHA-256 checksum is published with the stable release.

The published executable is unsigned, so Windows SmartScreen or antivirus reputation warnings can occur even when the published checksum matches.

GitHub Actions artifacts are build/validation outputs rather than the permanent customer distribution channel. Official customer downloads are GitHub Release assets.

## Security posture

AegisLog is defensive and read-only. Findings, anomaly scores, correlations, confidence values, incident priorities, and ATT&CK mappings are investigative signals rather than proof of compromise or attribution.

The application does not automatically modify accounts, firewall rules, services, telemetry sources, or host configuration.

## Release status

- **Published stable:** v2.0.1
- **Release target commit:** `c6b66083105116047c2a8471d7f1333f4cbe2b4f`
- **Windows artifacts:** `AegisLog.exe` and `AegisLog.exe.sha256`

See [`RELEASE_V2.0.1.md`](RELEASE_V2.0.1.md), [`ROADMAP.md`](ROADMAP.md), and the repository [`CHANGELOG.md`](../CHANGELOG.md) for details.
