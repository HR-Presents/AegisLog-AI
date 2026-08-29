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
- direct `stream`, `entities`, and `behavior` CLI commands
- versioned SQLite schema migration framework
- entity-index schema for future persisted correlation
- bounded finding retention during streaming analysis
- reproducible synthetic streaming benchmark harness
- CLI-registration and migration regression tests
- package entrypoint separated from the legacy command module for safer command growth

## V0.8 — Planned release engineering
- persist correlated entities into the entity index
- configuration schema versioning and migration
- declarative parser extensions
- release artifact verification and checksums
- signed tags / release attestations where supported
- benchmark thresholds and large-fixture regression jobs
- installation/update/uninstall lifecycle polish

## V1.0 target
A stable defensive terminal platform with documented detection semantics, privacy-preserving optional AI, extensible collectors/parsers, persistent investigation state, strong tests, release artifacts, and clear operational limitations.
