# Project status

AegisLog is a released, terminal-first defensive security platform. The current published stable release is **v2.1.3**.

## Current capabilities

- Local-first log analysis with deterministic defensive detections.
- Static analysis, live monitoring, and multi-source monitoring workflows.
- Windows Event Log, journald, Docker, and file-based defensive collection where supported.
- Incident correlation, investigation timelines, entity intelligence, MITRE ATT&CK context, anomaly scoring, evidence-led explanations, and analyst triage summaries.
- Persistent investigation/case history and bounded analysis workflows.
- Declarative JSON detection rules and structured parsing.
- Secret/privacy redaction, terminal sanitization, defensive data-handling boundaries, and read-only operation.
- Structured reports, baselines, behavior comparison, hunting, and indicator extraction.
- Automated CI, security checks, package builds, Windows one-file executable builds, smoke tests, lock audits, checksums, and guarded release publication.

AI Analyst and remote-provider workflows are not part of the supported public v2 product surface.

## v2.1 stable status

v2.1.0 strengthened reliability and evaluation evidence. v2.1.1 and v2.1.2 refined Windows terminal behavior. v2.1.3 shipped the Falcon/compact-Analyze presentation changes while intentionally preserving the deterministic investigation engine and read-only security model.

The guarded v2.1.3 release workflow completed successfully on release target commit `c01247b34a2dd54c863dd142c618f03e184af8f8`, publishing the standalone Windows executable and matching checksum.

## Windows visual acceptance status

The published v2.1.3 executable was subsequently reviewed in a real maximized Windows Terminal and **did not pass visual acceptance**. A later unreleased Mission Control experiment on `main` also failed visual review. Automated layout tests and a green Windows executable build are therefore treated as necessary engineering checks, not proof that a terminal composition is visually accepted.

No newer release should be inferred from development commits or CI artifacts. The current public release remains v2.1.3 until a separately prepared release is explicitly published.

## Correctness carried forward

The active v2 line preserves hardening for streaming correlation, timestamp-based authentication windows, source/account/host parsing, IPv4/IPv6 validation, out-of-order events, bounded state, and deterministic regression evaluation.

## Windows distribution

The primary Windows release artifact is a standalone `AegisLog.exe`; Python and a virtual environment are not required for the released executable. A matching `AegisLog.exe.sha256` checksum is published with the stable release.

The v2.1.3 executable SHA-256 is:

`1ddda99e03fd36ba1816b1567a28b8cc23d410583f34771c1287f9e3c1a28155`

The published executable is unsigned, so Windows SmartScreen or antivirus reputation warnings can occur even when the published checksum matches.

GitHub Actions artifacts are build/validation outputs rather than the permanent customer distribution channel. Official customer downloads are GitHub Release assets.

## Security posture

AegisLog is defensive and read-only. Findings, anomaly scores, correlations, confidence values, incident priorities, and ATT&CK mappings are investigative signals rather than proof of compromise or attribution.

The application does not automatically modify accounts, firewall rules, services, telemetry sources, or host configuration.

## Release status

- **Published stable:** v2.1.3
- **Published release target commit:** `c01247b34a2dd54c863dd142c618f03e184af8f8`
- **Windows artifacts:** `AegisLog.exe` and `AegisLog.exe.sha256`
- **Windows executable SHA-256:** `1ddda99e03fd36ba1816b1567a28b8cc23d410583f34771c1287f9e3c1a28155`
- **Windows visual acceptance:** not accepted after post-release real-Windows review
- **Evaluation boundary:** maintained benchmark corpora are synthetic regression evidence, not independently validated real-world effectiveness evidence

See [`RELEASE_V2.1.3.md`](RELEASE_V2.1.3.md), [`ROADMAP.md`](ROADMAP.md), and the repository [`CHANGELOG.md`](../CHANGELOG.md) for details.
