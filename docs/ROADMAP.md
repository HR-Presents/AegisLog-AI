# Roadmap

## V0.2 — intelligence foundation

Structured parsing, live watch, local anomaly scoring, incident correlation, local question-driven investigation, configuration, install helpers, security policy, and CI coverage.

## V0.3 — provider and telemetry adapters

- optional remote AI provider adapter with explicit opt-in and redacted/minimized context
- local-model adapter
- journald command adapter
- Docker/container log adapter
- Nginx/Apache-specific normalization
- configurable detection thresholds and allowlists
- persisted incident store

## V0.4 — analyst workflow

- incident detail and timeline commands
- baseline comparison across time windows
- richer explainability and confidence metadata
- SARIF/JSONL export
- plugin interface for parsers and rules

## V1.0 — stable terminal platform

Stable CLI/API contracts, packaging/release automation, expanded test corpus, documented threat model, performance limits, and upgrade/migration guarantees.
