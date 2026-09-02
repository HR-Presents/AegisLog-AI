# Roadmap

AegisLog AI is currently released as **v1.5.0**. Stable release work stays on `main`; new feature development is isolated on `develop/v1.6.0` and feature branches based from it.

## Completed foundation

The V0.1–V1.0 foundation delivered the terminal CLI, deterministic detections, structured parsing, redaction, live monitoring, anomaly scoring, incident correlation, persistent investigation state, native collection, declarative rules, bounded-memory analysis, reporting, CI/security hardening, package validation, and reproducible release engineering.

## Current stable line — v1.5.x

### v1.5.0 — current stable release

v1.5.0 strengthened daily analyst workflows without changing AegisLog's defensive boundaries.

- Ordered analyst next actions across incidents and investigations.
- Runtime-aware command examples for source installs and frozen Windows builds.
- Shared semantic terminal styling for severity, confidence, incidents, anomalies, and evidence.
- Consistent live-monitoring startup/status UX across single-file, multi-source, and native modes.
- Immediate initial live results preserved before continuous refresh.
- Clear read-only and safe Ctrl+C operator guidance.
- Bounded trend-history aggregation for high-frequency workloads.
- Stress-style regression coverage and a dedicated live-state benchmark.
- Version-locked package, customer-bundle, and guarded release metadata.
- Standalone Windows `AegisLog.exe` plus SHA-256 checksum delivery.

## Active development line — v1.6.x

The v1.6 line should focus on deeper analyst productivity, trustworthy local telemetry handling, and long-running operational reliability rather than adding broad new attack-oriented capabilities.

### Priority 1 — investigation workspace quality

- Make incident-to-investigation navigation faster and more consistent.
- Improve timeline grouping, evidence readability, entity context, and analyst next-action continuity.
- Add safer export/report ergonomics for sharing sanitized investigation results.
- Keep all explanations evidence-led and explicitly non-attributive.

### Priority 2 — live monitoring resilience

- Continue bounded-resource hardening for long-running single-file, multi-source, and native monitoring.
- Add stronger regression coverage around source rotation, temporary source loss, empty reads, and recovery.
- Improve operator visibility into source health without changing the monitored host.
- Preserve immediate initial results and safe Ctrl+C shutdown behavior.

### Priority 3 — native telemetry quality

- Improve platform-specific diagnostics for Windows Event Log, journald, and Docker collectors.
- Add clearer supported/unsupported state reporting and actionable troubleshooting guidance.
- Keep collectors bounded and read-only; no service, firewall, account, or host-configuration changes.

### Priority 4 — release and distribution trust

- Evaluate practical Windows code-signing options without making signing a hard requirement for development builds.
- Keep checksum-first verification and immutable-style release safeguards.
- Reduce opportunities for release metadata, documentation, and package names to drift out of sync.

### Priority 5 — performance and test depth

- Expand benchmark coverage for sustained event rates and multi-source correlation workloads.
- Add regression tests for pathological high-volume input while preserving bounded memory behavior.
- Profile expensive terminal rendering or correlation paths before optimizing them.

### Priority 6 — optional AI boundaries

- Keep deterministic local analysis as the primary workflow.
- Any optional AI assistance must remain opt-in, minimized/redacted, and secondary to local evidence.
- Do not treat generated explanations as proof, attribution, or autonomous remediation decisions.

## Non-goals

v1.6.x should not introduce exploitation, malware, credential theft, persistence, evasion, destructive actions, automatic remediation, or tooling intended to compromise systems. AegisLog remains a defensive, local-first, read-only investigation platform.
