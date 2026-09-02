# Roadmap

AegisLog AI is currently released as **v1.6.0**. Stable release work stays on `main`. New development should begin from a fresh development branch only when there is a concrete, reviewable goal; v1.6.0 itself is considered complete.

## Completed foundation

The V0.1–V1.0 foundation delivered the terminal CLI, deterministic detections, structured parsing, redaction, live monitoring, anomaly scoring, incident correlation, persistent investigation state, native collection, declarative rules, bounded-memory analysis, reporting, CI/security hardening, package validation, and reproducible release engineering.

## Current stable line — v1.6.x

### v1.6.0 — current stable release

v1.6.0 focused on analyst productivity, trustworthy local telemetry handling, and long-running operational reliability while preserving AegisLog's defensive boundaries.

- Added analyst triage summaries to investigation output using existing local severity, confidence, timeline, and entity evidence.
- Kept triage guidance explicitly non-attributive and non-conclusive.
- Improved Windows Event Log, journald, and Docker diagnostics by distinguishing unsupported sources from temporarily unavailable sources.
- Added source-specific, read-only troubleshooting guidance without changing host policy or collector permissions.
- Added one-time live source-loss and recovery visibility for single-file monitoring.
- Extended source-loss and recovery visibility to multi-source monitoring while preserving the current dashboard during temporary loss.
- Preserved safe cursor behavior when monitored files return, rotate, or are replaced.
- Aggregated multi-source arrival history by ingest batch rather than by individual line.
- Added hard bounds for arrival-history buckets and alert-fingerprint state.
- Added focused regressions for 50,000-line ingest batches, runtime-state ceilings, source recovery, native diagnostics, and analyst triage.
- Preserved deterministic local analysis, read-only collection, explicit uncertainty language, and no automatic remediation.
- Published the standalone Windows `AegisLog.exe` and matching SHA-256 checksum through the guarded v1.6.0 release workflow.

## Near-term maintenance priorities

The next work should be driven by real operator feedback and measurable reliability needs rather than version-number pressure.

### Reliability and support

- Fix reproducible defects found in v1.6.0 without changing the defensive product boundary.
- Keep source-loss, rotation, empty-read, and recovery regression coverage strong.
- Maintain hard bounds for long-running live and multi-source state.
- Profile performance before adding optimizations that could alter analysis semantics.

### Analyst workflow quality

- Improve investigation readability, timeline grouping, and evidence navigation when user feedback identifies specific friction.
- Improve sanitized export/report ergonomics without exposing unredacted telemetry by default.
- Keep incident priorities and explanations evidence-led, conservative, and explicitly non-attributive.

### Native telemetry quality

- Expand platform-specific diagnostics only where supported collectors can remain bounded and read-only.
- Keep unsupported/unavailable states clear and avoid troubleshooting steps that weaken host security controls.
- Validate Windows Event Log, journald, and Docker behavior against real supported environments as changes are made.

### Release and distribution trust

- Keep checksum-first verification and immutable-style release safeguards.
- Evaluate practical Windows code-signing options separately from ordinary development builds.
- Keep package versions, release notes, workflow names, documentation, and artifact names synchronized through regression tests.

### Optional AI boundaries

- Deterministic local analysis remains the primary workflow.
- Any optional AI assistance must remain opt-in, minimized/redacted, and secondary to local evidence.
- Generated explanations must not be treated as proof, attribution, or autonomous remediation decisions.

## Future development line

A future v1.7.x line should not be opened solely to add features. It should start only after one or more concrete goals are selected from operator feedback, reliability data, or clearly scoped defensive workflow improvements. When that happens, use a dedicated development branch and feature PRs before preparing any release candidate.

## Non-goals

Future AegisLog work should not introduce exploitation, malware, credential theft, persistence, evasion, destructive actions, automatic remediation, or tooling intended to compromise systems. AegisLog remains a defensive, local-first, read-only investigation platform.
