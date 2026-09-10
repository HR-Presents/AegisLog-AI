# Roadmap

AegisLog is currently released as **v2.0.0**. Stable release work stays reviewable on `main`; new development should begin from a fresh branch with a concrete, testable goal.

## Completed foundation

The V0.1–V2.0 foundation delivered the terminal CLI, deterministic detections, structured parsing, redaction, live monitoring, anomaly scoring, incident correlation, persistent investigation state, native collection, declarative rules, bounded-memory analysis, reporting, CI/security hardening, package validation, guarded release engineering, and a responsive Mission Control interface.

## Current stable line — v2.0.x

### v2.0.0 — current stable release

v2.0.0 focused on the operator experience while preserving the deterministic investigation engine hardened in v1.9.0.

- Rebuilt Mission Control as a responsive full-width workspace.
- Added balanced Investigation and Monitoring areas for wide terminals with clear narrow/medium fallbacks.
- Moved version and readiness status into the header hierarchy.
- Removed the duplicate fake `SELECT >` prompt so the real shell prompt is authoritative.
- Added explicit layout, Windows rendering, and ASCII-safety regression coverage.
- Preserved v1.9 streaming-correlation, authentication-window, parser, IPv4/IPv6, bounded-state, and synthetic regression hardening without changing detection semantics.
- Kept AI Analyst and remote-provider workflows out of the supported public product surface.
- Published the standalone Windows `AegisLog.exe` and matching SHA-256 checksum through the guarded v2.0.0 release workflow.

## Near-term maintenance priorities

The next work should be driven by operator feedback, measurable reliability needs, and evidence rather than version-number pressure.

### Reliability and correctness

- Expand real-world, independently labeled evaluation beyond the maintained synthetic regression corpus.
- Add property-based and fuzz testing around parsers, timestamp ordering, correlation boundaries, and malformed input.
- Keep streaming results independent of chunk boundaries and maintain bounded state under long-running workloads.
- Profile performance before making optimizations that could alter detection semantics.

### Analyst workflow quality

- Improve investigation readability, evidence navigation, and report ergonomics where verified user feedback identifies friction.
- Keep incident priorities and explanations evidence-led, conservative, and explicitly non-attributive.
- Preserve responsive terminal behavior across Windows, Linux, and macOS terminal environments.

### Native telemetry quality

- Expand platform-specific diagnostics only where supported collectors can remain bounded and read-only.
- Keep unsupported/unavailable states clear and avoid troubleshooting steps that weaken host security controls.
- Validate Windows Event Log, journald, and Docker behavior against real supported environments as changes are made.

### Release and distribution trust

- Keep checksum-first verification and fail-closed release safeguards.
- Evaluate practical Windows code-signing options separately from ordinary development builds.
- Keep package versions, release notes, workflow names, documentation, public branding, and artifact names synchronized through regression tests.
- Preserve historical release workflows and notes as immutable release records rather than rewriting prior versions.

## Future development line

A future v2.1.x line should begin only after one or more concrete goals are selected from operator feedback, evaluation evidence, reliability data, or clearly scoped defensive workflow improvements.

## Non-goals

Future AegisLog work should not introduce exploitation, malware, credential theft, persistence, evasion, destructive actions, automatic remediation, or tooling intended to compromise systems. AegisLog remains a defensive, local-first, read-only investigation platform.
