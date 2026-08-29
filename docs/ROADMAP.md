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
- multi-window behavioral profiling for level/source/time shifts
- entity correlation across IP, host, user, service, and container evidence
- bounded-memory streaming analysis for large files
- correlation/streaming/behavior regression tests
- CI lint scope focused on correctness errors while tests validate behavior

## V0.7 — Planned release hardening
- database schema migrations and richer evidence/entity indexing
- expose entity graph, behavioral windows, and streaming mode throughout CLI/reporting
- declarative parser extension interface
- performance benchmarks and large-fixture tests
- signed/reproducible release pipeline
- stable configuration schema and migration policy

## V1.0 target
A stable defensive terminal platform with documented detection semantics, privacy-preserving optional AI, extensible collectors/parsers, persistent investigation state, strong tests, release artifacts, and clear operational limitations.
