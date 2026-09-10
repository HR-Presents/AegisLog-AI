# Project status

AegisLog is a released, terminal-first defensive security platform. The current published stable release is **v2.0.1**. The **v2.1 development line is active on `main`** and is in release-readiness review; it is not yet a published release.

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

## v2.1 development status

The current v2.1 work is reliability- and evidence-focused rather than a detection-semantic rewrite:

- deterministic fuzz-style regressions cover malformed input, randomized stream chunking, authentication event reordering, and bounded source floods;
- the external detection-evidence format uses schema v2 with explicit provenance, source types, collection period, sampling method, known exclusions, class balance, category counts, per-category metrics, and confidence intervals;
- a broader representative synthetic benchmark corpus supplements the core regression fixture with benign controls, near-miss cases, authentication variants, and coverage across audit, error, network, privilege, service, and web detections;
- synthetic benchmark results remain regression evidence only and must not be represented as deployment-specific or independently validated real-world effectiveness.

These changes preserve the existing read-only product model and do not by themselves justify a v2.1.0 release until the release-preparation branch, exact-head quality gates, packaging checks, and guarded release workflow are completed.

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

The active v2 line preserves the v1.9 hardening for streaming correlation, timestamp-based authentication windows, source/account/host parsing, IPv4/IPv6 validation, out-of-order events, bounded state, and deterministic regression evaluation.

## Windows distribution

The primary Windows release artifact is a standalone `AegisLog.exe`; Python and a virtual environment are not required for the released executable. A matching SHA-256 checksum is published with the stable release.

The published executable is unsigned, so Windows SmartScreen or antivirus reputation warnings can occur even when the published checksum matches.

GitHub Actions artifacts are build/validation outputs rather than the permanent customer distribution channel. Official customer downloads are GitHub Release assets.

## Security posture

AegisLog is defensive and read-only. Findings, anomaly scores, correlations, confidence values, incident priorities, and ATT&CK mappings are investigative signals rather than proof of compromise or attribution.

The application does not automatically modify accounts, firewall rules, services, telemetry sources, or host configuration.

## Release status

- **Published stable:** v2.0.1
- **Published release target commit:** `c6b66083105116047c2a8471d7f1333f4cbe2b4f`
- **Development line:** v2.1 release-readiness review on `main`
- **Windows artifacts for current stable:** `AegisLog.exe` and `AegisLog.exe.sha256`

See [`RELEASE_V2.0.1.md`](RELEASE_V2.0.1.md), [`ROADMAP.md`](ROADMAP.md), and the repository [`CHANGELOG.md`](../CHANGELOG.md) for details.
