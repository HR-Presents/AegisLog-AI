# AegisLog v2.1.3

AegisLog v2.1.3 is a Windows-terminal acceptance patch focused on the real rendered operator experience observed after v2.1.2.

## What changed

- Replaced the generic Shield-A terminal mark with the approved front-facing Falcon identity.
- Removed the competing legacy masthead signature so Mission Control has one clear brand mark.
- Kept Mission Control terminal-first, bounded, responsive, ASCII-safe, and compatible with Windows console rendering.
- Reworked Analyze Log into a compact prioritized summary instead of printing every timeline, finding, anomaly, telemetry, and raw-evidence table by default.
- Retained top findings, Analyst Focus, source context, metrics, next investigation actions, and automatic local HTML report generation.
- Preserved deep forensic evidence in the generated HTML report and existing incident/investigation commands rather than hiding or discarding it.
- Added acceptance regressions for the Falcon identity, removal of the old signature, bounded wide-terminal output, and the compact Analyze summary.

## Security and behavior boundaries

This patch does not change detection rules, parser semantics, streaming behavior, authentication correlation, incident-correlation semantics, evidence handling, or the local-first/read-only security model.

No mock security results or fabricated telemetry were introduced. The terminal summary only presents data already produced by AegisLog's deterministic analysis path.

AI Analyst remains removed from the public product surface. Deterministic local investigation commands remain authoritative.

## Windows executable

The release workflow builds a single-file `AegisLog.exe` and `AegisLog.exe.sha256`, verifies the checksum before publication, and emits build provenance attestation for the executable.

The Windows executable is **not Authenticode-signed**. Verify the published SHA-256 checksum and GitHub release provenance before use.

## Validation scope

Release publication is gated on CI, security checks, locked dependency audits, package build, Windows single-executable build, synthetic detection regression gates, and executable smoke tests covering Mission Control, the Falcon identity, compact Analyze output, and removed AI surfaces.

Synthetic evaluation remains regression evidence only and is not a claim of real-world detection effectiveness.
