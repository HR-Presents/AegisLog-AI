# Roadmap

AegisLog AI has progressed beyond its original pre-1.0 roadmap and is currently released as **v1.4.6**.

## Completed foundation

The original V0.1–V1.0 roadmap delivered the terminal CLI, deterministic detections, structured parsing, redaction, live monitoring, anomaly scoring, incident correlation, persistent investigation state, native collection, declarative rules, bounded-memory analysis, reporting, CI/security hardening, package validation, and reproducible release engineering.

## Current stable line — v1.4.x

The v1.4.x line focuses on Windows terminal usability, one-file distribution, live SOC workflows, incident explanation quality, release reliability, and product polish.

### v1.4.6 — current stable release

- Immediate initial dashboard rendering for live single-file monitoring.
- Immediate initial correlated dashboard rendering for multi-source monitoring.
- Immediate initial snapshot rendering for native live monitoring.
- Improved semantic terminal colors for incident explanations.
- Regression coverage for live rendering and incident explanation presentation.
- Version-locked, manually guarded Windows release workflow with smoke tests and SHA-256 release assets.

## Next development line — v1.5.x

The next minor release should prioritize improvements that materially strengthen day-to-day defensive use rather than another cosmetic patch.

Candidate priorities:

- Improve analyst workflow ergonomics across dashboard, incidents, investigation, and live monitoring.
- Strengthen Windows distribution trust and release verification, including evaluating code-signing options.
- Expand practical regression coverage for native telemetry and long-running live workflows.
- Improve documentation freshness and make release/current-status metadata easier to keep synchronized.
- Continue performance and bounded-resource hardening for larger local datasets.
- Keep optional AI integrations privacy-preserving and secondary to deterministic local analysis.

Any v1.5.x feature work should preserve AegisLog's defensive, local-first, read-only security model.
