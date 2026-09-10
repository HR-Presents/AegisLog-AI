# Project status

AegisLog is a released, terminal-first defensive security platform. The current published stable release is **v2.1.1**.

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

AI Analyst and remote-provider workflows are not part of the supported public v2 product surface.

## v2.1 stable status

v2.1.0 strengthened reliability and evidence quality without a detection-semantic rewrite, while v2.1.1 is a focused terminal UI polish patch based on real Windows rendered output:

- deterministic fuzz-style regressions cover malformed input, randomized stream chunking, authentication event reordering, and bounded source floods;
- the external detection-evidence format uses schema v2 with explicit provenance, source types, collection period, sampling method, known exclusions, class balance, category counts, per-category metrics, and confidence intervals;
- a broader representative synthetic benchmark corpus supplements the core regression fixture with benign controls, near-miss cases, authentication variants, and coverage across audit, error, network, privilege, service, and web detections;
- v2.1.1 bounds Mission Control on wide Windows terminals, improves investigation/monitoring hierarchy, simplifies system actions, and preserves ASCII/cp1252-safe rendering;
- synthetic benchmark results remain regression evidence only and must not be represented as deployment-specific or independently validated real-world effectiveness.

The guarded v2.1.1 release workflow completed successfully on release target commit `31dbb523bd79959738b3a5e2a7ffc0ec6f5ceea2`, publishing the standalone Windows executable and matching checksum. The release preserves detection, parsing, streaming, authentication, correlation, monitoring, evidence handling, and the existing read-only product model.

## Current v2 UI

v2.0.0 rebuilt Mission Control around a clearer operator hierarchy. v2.0.1 corrected public branding and release-status surfaces. v2.1.0 carried that experience forward while hardening reliability and evaluation evidence, and v2.1.1 refined the real Windows terminal composition:

- bounded wide-terminal layout rather than stretching across all available columns;
- separate Investigation and Monitoring operator work areas;
- compact System actions and simplified navigation footer;
- consistent AegisLog workspace headers and shared page chrome;
- version and readiness status integrated into the header hierarchy;
- the duplicate fake `SELECT >` prompt remains removed so the real shell prompt is authoritative;
- ASCII-safe structural chrome with explicit Windows rendering regression coverage.

## Correctness carried forward from v1.9

The active v2 line preserves the v1.9 hardening for streaming correlation, timestamp-based authentication windows, source/account/host parsing, IPv4/IPv6 validation, out-of-order events, bounded state, and deterministic regression evaluation.

## Windows distribution

The primary Windows release artifact is a standalone `AegisLog.exe`; Python and a virtual environment are not required for the released executable. A matching `AegisLog.exe.sha256` checksum is published with the stable release.

The v2.1.1 executable SHA-256 is `61fc07de08a0597a350ed4438f838f29ae5ff616f58c86774d8bc059abcf2b1c`.

The published executable is unsigned, so Windows SmartScreen or antivirus reputation warnings can occur even when the published checksum matches.

GitHub Actions artifacts are build/validation outputs rather than the permanent customer distribution channel. Official customer downloads are GitHub Release assets.

## Security posture

AegisLog is defensive and read-only. Findings, anomaly scores, correlations, confidence values, incident priorities, and ATT&CK mappings are investigative signals rather than proof of compromise or attribution.

The application does not automatically modify accounts, firewall rules, services, telemetry sources, or host configuration.

## Release status

- **Published stable:** v2.1.1
- **Published release target commit:** `31dbb523bd79959738b3a5e2a7ffc0ec6f5ceea2`
- **Windows artifacts for current stable:** `AegisLog.exe` and `AegisLog.exe.sha256`
- **Windows executable SHA-256:** `61fc07de08a0597a350ed4438f838f29ae5ff616f58c86774d8bc059abcf2b1c`
- **Evaluation boundary:** maintained benchmark corpora are synthetic regression evidence, not independently validated real-world effectiveness evidence

See [`RELEASE_V2.1.1.md`](RELEASE_V2.1.1.md), [`ROADMAP.md`](ROADMAP.md), and the repository [`CHANGELOG.md`](../CHANGELOG.md) for details.
