# Roadmap

AegisLog is currently released as **v2.1.3**.

## Completed foundation

The V0.1–V2.0 foundation delivered the terminal CLI, deterministic detections, structured parsing, redaction, live monitoring, anomaly scoring, incident correlation, persistent investigation state, native collection, declarative rules, bounded-memory analysis, reporting, CI/security hardening, package validation, guarded release engineering, and a responsive Mission Control interface.

## Current stable line — v2.1.x

### v2.1.3 — current published release

v2.1.3 shipped a Windows presentation update while preserving the v2.1 correctness and evidence foundations.

- Falcon/compact-Analyze presentation work was released without changing detection, parsing, streaming, authentication, incident-correlation, monitoring, evidence, or read-only security semantics.
- The guarded v2.1.3 workflow published `AegisLog.exe` and its matching SHA-256 checksum from target commit `c01247b34a2dd54c863dd142c618f03e184af8f8`.
- The released Windows EXE SHA-256 is `1ddda99e03fd36ba1816b1567a28b8cc23d410583f34771c1287f9e3c1a28155`.
- The executable remains unsigned.
- Synthetic benchmark results remain regression evidence only.

### Visual acceptance lesson

Post-release review of v2.1.3 in a real maximized Windows Terminal showed that the Mission Control composition did **not** meet the desired visual standard. A subsequent unreleased UI experiment also failed review. Future presentation work should not be called visually accepted solely because automated rendering, package, or Windows build checks pass.

No new UI release should be prepared unless there is a deliberate product decision to resume that work and a real-Windows capture has been reviewed first.

### v2.1.0–v2.1.2 — reliability and terminal hardening

The earlier v2.1 releases strengthened deterministic fuzz regressions, external-evidence schema quality, representative synthetic benchmark coverage, Windows terminal bounds, and release engineering without intentionally rewriting core detection semantics.

## Near-term maintenance priorities

### Reliability and correctness

- Expand real-world, independently labeled evaluation when suitable authorized data is available.
- Continue parser/correlation fuzz and property-style regression coverage where concrete edge cases are identified.
- Keep streaming results independent of chunk boundaries and maintain bounded state under long-running workloads.
- Profile performance before making optimizations that could alter detection semantics.

### Analyst workflow quality

- Improve evidence navigation and report ergonomics only where verified operator feedback identifies friction.
- Keep incident priorities and explanations evidence-led, conservative, and explicitly non-attributive.
- Preserve responsive terminal behavior across supported environments.
- Treat real terminal captures as the final visual-acceptance evidence for presentation changes.

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
