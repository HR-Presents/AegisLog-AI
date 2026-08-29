# Roadmap

## V0.1 — Foundation
Installable terminal CLI, deterministic security/error rules, secret redaction, JSON reporting, initial CI and tests.

## V0.2 — Intelligence layer
Structured parsing, live watch, anomaly scoring, incident correlation, local investigation, and security/privacy documentation.

## V0.3 — AI and collection layer
Optional compatible AI and Ollama adapters, prompt-injection boundary, remote provider protection, bounded journald/Docker collectors, history, and local fallback.

## V0.4 — Analyst workflow
SQLite incident/evidence index, drill-down and timeline, baseline comparison, HTML/Markdown reports, and safer report rendering.

## V0.5 — SOC hunting and extensibility
Persisted hunting, defensive indicator extraction, declarative JSON rule packs, plugin-aware analysis, and expanded tests.

## V0.6 — Scale and correlation
Multi-window behavioral profiling, entity correlation across IP/host/user/service/container evidence, bounded-memory streaming analysis, and regression tests.

## V0.7 — Release hardening
Direct scale CLI commands, versioned SQLite migrations, future-schema rejection, streaming retention bounds, benchmark harness, and stabilized CI/security/package builds.

## V0.8 — Persistent correlation
- persisted entity graph and historical entity pivots
- ranked entity investigation across incidents
- stateful bounded-window live correlation
- hardened Rich terminal rendering for log-derived text
- JSON report schema/tool/timestamp metadata
- SPDX-style package license metadata

## V0.9 — Final release candidate hardening
- configuration schema versioning and migration
- declarative parser extensions
- richer redaction for authorization headers, JWTs, emails and optional IP privacy
- large-fixture regression/performance jobs
- installation/update/uninstall lifecycle polish
- release artifact verification and checksums
- final documentation and detection-semantics audit

## V1.0 target
Stable defensive terminal platform with documented detection semantics, privacy-preserving optional AI, extensible collection/parsing, persistent investigation state, reproducible release artifacts, strong automated tests, and clear operational limitations.
