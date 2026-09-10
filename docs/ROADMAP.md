# Roadmap

AegisLog is currently released as **v2.0.1**. The **v2.1 development line is active on `main`** and is in release-readiness review; v2.1.0 has not yet been published.

## Completed foundation

The V0.1–V2.0 foundation delivered the terminal CLI, deterministic detections, structured parsing, redaction, live monitoring, anomaly scoring, incident correlation, persistent investigation state, native collection, declarative rules, bounded-memory analysis, reporting, CI/security hardening, package validation, guarded release engineering, and a responsive Mission Control interface.

## Current stable line — v2.0.x

### v2.0.1 — current stable release

v2.0.1 is the public-surface consistency patch for the v2 line. It keeps the v2.0.0 Mission Control redesign and v1.9 correctness hardening unchanged while aligning the supported CLI, customer bundle, README examples, and current-status documentation with the AegisLog product identity.

### v2.0.0 — terminal experience foundation

v2.0.0 focused on the operator experience while preserving the deterministic investigation engine hardened in v1.9.0.

- Rebuilt Mission Control as a responsive full-width workspace.
- Added balanced Investigation and Monitoring areas for wide terminals with clear narrow/medium fallbacks.
- Moved version and readiness status into the header hierarchy.
- Removed the duplicate fake `SELECT >` prompt so the real shell prompt is authoritative.
- Added explicit layout, Windows rendering, and ASCII-safety regression coverage.
- Preserved v1.9 streaming-correlation, authentication-window, parser, IPv4/IPv6, bounded-state, and synthetic regression hardening without changing detection semantics.
- Kept AI Analyst and remote-provider workflows out of the supported public product surface.
- Published the standalone Windows `AegisLog.exe` and matching SHA-256 checksum through the guarded v2.0 release workflows.

## Active development line — v2.1.x

v2.1 is focused on reliability evidence and release confidence rather than expanding attack capability or silently changing detector semantics.

### Completed v2.1 hardening

- Added deterministic fuzz-style regressions around malformed input, randomized streaming chunk boundaries, authentication-event ordering, and bounded authentication-source floods.
- Strengthened external detection evidence to schema v2 with explicit provenance fields, source types, collection period, sampling method, known exclusions, class balance, category counts, per-category metrics, and confidence intervals.
- Added a broader representative synthetic benchmark corpus with benign controls, near-miss cases, authentication variants, and category coverage across audit, error, network, privilege, service, and web detections.
- Kept the larger benchmark explicitly labeled as synthetic regression evidence rather than real-world effectiveness proof.

### Release-readiness gate for v2.1.0

Before v2.1.0 can be published:

- synchronize package/version metadata, changelog, release notes, documentation, and workflow naming;
- build the dedicated guarded v2.1.0 release workflow;
- run the full required exact-head quality set: CI, Security checks, Package build, Windows single executable, Runtime lock audit, Validation toolchain lock audit, and Build toolchain lock audit;
- verify the release candidate introduces no unintended detection, parsing, streaming, authentication, monitoring, or read-only security-model changes;
- verify the Windows executable, checksum, smoke tests, and final GitHub Release assets after publication.

Independent real-world evaluation remains valuable but must use genuinely authorized, sanitized, independently labeled external data. It must not be fabricated as a release checkbox.

## Near-term maintenance priorities

The next work should be driven by operator feedback, measurable reliability needs, and evidence rather than version-number pressure.

### Reliability and correctness

- Expand real-world, independently labeled evaluation beyond the maintained synthetic regression corpus when suitable authorized data is available.
- Continue parser/correlation fuzz and property-style regression coverage where concrete edge cases are identified.
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

## Non-goals

Future AegisLog work should not introduce exploitation, malware, credential theft, persistence, evasion, destructive actions, automatic remediation, or tooling intended to compromise systems. AegisLog remains a defensive, local-first, read-only investigation platform.
