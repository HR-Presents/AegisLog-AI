# Roadmap

## V0.1 — Foundation

Installable terminal CLI, deterministic security/error rules, secret redaction, JSON reporting, initial CI and tests.

## V0.2 — Intelligence layer

Structured generic/syslog/journald/web parsing, live file watch, lightweight anomaly scoring, incident correlation, local question-driven investigation, and security/privacy documentation.

## V0.3 — AI and collection layer

Optional compatible AI and Ollama adapters, prompt-injection boundary, remote provider network protection, bounded journald/Docker collectors, incident history, and local fallback.

## V0.4 — Analyst workflow

SQLite-backed incident/evidence index, incident drill-down and timeline, baseline comparison, analyst-ready HTML/Markdown reports, and safer report rendering.

## V0.5 — SOC hunting and extensibility

- persisted incident hunting by text, severity, category, and source
- defensive IP/domain indicator extraction
- declarative JSON rule packs with failure isolation and no plugin code execution
- plugin-aware analysis workflow
- expanded tests for plugins and hunting primitives

## V0.6 — Planned scale and correlation

- time-window behavioral baselines rather than sample-only comparisons
- entity correlation across IP, host, user, service, and container
- database schema migrations and richer evidence indexing
- streaming analysis for large files without full-file reads
- declarative parser extension interface
- signed/reproducible release pipeline

## V1.0 target

A stable defensive terminal platform with documented detection semantics, privacy-preserving optional AI, extensible collectors/parsers, persistent investigation state, strong tests, release artifacts, and clear operational limitations.
