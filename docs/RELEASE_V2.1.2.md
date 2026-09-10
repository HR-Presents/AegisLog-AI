# AegisLog v2.1.2

AegisLog v2.1.2 is a terminal-first security command-center polish release built on the existing AegisLog architecture and workflows.

## What changed

- Adopted the Shield A terminal identity while preserving the established AegisLog terminal signature and Windows-safe ASCII rendering.
- Refined Mission Control into stronger INVESTIGATE, MONITOR, and SYSTEM work areas without changing numbered commands or command behavior.
- Upgraded Analyze Log presentation with compact real-data security metrics, severity/category distributions, timestamp-aware activity visualization, investigation timelines, stronger Analyst Focus, improved incident/finding tables, and readable raw evidence.
- Added data-aware live-monitor presentation using existing realtime state: live metrics, severity/service distributions, trend context, recent findings, and status information.
- Added multi-source source-activity visualization and alert presentation using existing MultiSourceState data only.
- Reworked Health and Help pages into consistent AegisLog command-center panels while preserving actual capability and source availability behavior.
- Improved responsive rendering across narrow, normal, and wide terminal widths, including Windows cp1252-safe output.

## What did not change

This release does not change detection rules, parser semantics, authentication correlation, streaming correctness, incident-correlation semantics, evidence handling, or the local-first/read-only security model.

No mock security results or fabricated telemetry were introduced. Visualizations are rendered only from data already available to AegisLog, and timestamp-based visualizations are omitted when timestamp data is insufficient.

AI Analyst remains removed from the public product surface. Deterministic local investigation commands remain authoritative.

## Windows executable

The release workflow produces a single-file `AegisLog.exe` and `AegisLog.exe.sha256`, verifies the checksum before publication, and emits build provenance attestation for the executable.

The Windows executable is **not Authenticode-signed**. Users should verify the published SHA-256 checksum and GitHub release provenance before use.

## Validation scope

Release publication is gated on CI, security checks, locked dependency audits, package build, Windows single-executable build, synthetic detection regression gates, and release smoke tests. The Windows release smoke test also exercises Mission Control and Analyze Log so the command-center changes are included in executable validation.

Synthetic evaluation remains regression evidence only and is not a claim of real-world detection effectiveness.
