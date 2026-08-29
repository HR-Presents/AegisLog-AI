# Roadmap

## V0.1 — Foundation

Installable terminal CLI, deterministic security/error rules, secret redaction, JSON reporting, initial CI and tests.

## V0.2 — Intelligence layer

Structured generic/syslog/journald/web parsing, live file watch, lightweight anomaly scoring, incident correlation, local question-driven investigation, and security/privacy documentation.

## V0.3 — AI and collection layer

- optional OpenAI-compatible provider adapter
- explicit local Ollama adapter
- prompt-injection boundary for untrusted telemetry
- remote provider private-network protection
- bounded journald collector
- bounded Docker logs collector
- persistent incident history
- AI-provider fallback to local analysis

## V0.4 — Planned analyst workflow

- richer statistical baselines over time windows
- SQLite-backed incident/evidence index
- incident timeline drill-down
- pluggable parser/rule packs
- richer Docker/systemd metadata correlation
- analyst-ready HTML/Markdown reports
- performance work for large files and streaming workloads
- signed/reproducible release pipeline

## V1.0 target

A stable defensive terminal platform with documented detection semantics, privacy-preserving optional AI, extensible collectors/parsers, persistent investigation state, strong tests, release artifacts, and clear operational limitations.
