# Roadmap

AegisLog is currently released as **v2.1.1**.

## Completed foundation

The V0.1–V2.0 foundation delivered the terminal CLI, deterministic detections, structured parsing, redaction, live monitoring, anomaly scoring, incident correlation, persistent investigation state, native collection, declarative rules, bounded-memory analysis, reporting, CI/security hardening, package validation, guarded release engineering, and a responsive Mission Control interface.

## Current stable line — v2.1.x

### v2.1.1 — current stable release

v2.1.1 is a focused Windows terminal UI polish patch built from real rendered output while preserving the v2.1 reliability and evidence hardening.

- Bounded Mission Control on wide Windows terminals instead of stretching across all available columns.
- Reworked investigation and monitoring actions into separate operator work areas with clearer hierarchy and shorter descriptions.
- Compressed System actions into a compact command row and simplified the navigation footer.
- Preserved ASCII/cp1252-safe output, version/readiness status, the single authoritative prompt, and the public removal of AI Analyst.
- Preserved detection, parsing, streaming, authentication, incident correlation, monitoring semantics, evidence handling, and read-only security behavior.
- Passed the required exact-head CI, security, package-build, Windows executable, and dependency-lock checks before release preparation was merged.
- Passed the guarded v2.1.1 release workflow on target commit `31dbb523bd79959738b3a5e2a7ffc0ec6f5ceea2` and published `AegisLog.exe` with its matching SHA-256 checksum.

### v2.1.0 — reliability and evidence foundation

v2.1.0 strengthened reliability and evaluation evidence without intentionally changing detection, parsing, streaming, authentication, monitoring, or read-only security semantics.

- Added deterministic fuzz-style regressions around malformed input, randomized streaming chunk boundaries, authentication-event ordering, and bounded authentication-source floods.
- Strengthened external detection evidence to schema v2 with explicit provenance fields, source types, collection period, sampling method, known exclusions, class balance, category counts, per-category metrics, and confidence intervals.
- Added a broader representative synthetic benchmark corpus with benign controls, near-miss cases, authentication variants, and category coverage across audit, error, network, privilege, service, and web detections.
- Kept the larger benchmark explicitly labeled as synthetic regression evidence rather than real-world effectiveness proof.

Independent real-world evaluation remains valuable but must use genuinely authorized, sanitized, independently labeled external data. It must not be fabricated as a release checkbox or implied by the synthetic regression results.

## Previous stable line — v2.0.x

### v2.0.1 — public-surface consistency patch

v2.0.1 kept the v2.0.0 Mission Control redesign and v1.9 correctness hardening unchanged while aligning the supported CLI, customer bundle, README examples, and current-status documentation with the AegisLog product identity.

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
