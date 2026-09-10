# AegisLog v2.0.0

AegisLog v2.0.0 is a terminal experience release focused on making Mission Control feel like a deliberate, production-grade console while preserving the deterministic, local-first defensive investigation engine hardened in v1.9.0.

## Highlights

- Rebuilds Mission Control into a responsive, full-width terminal workspace instead of a sparse left-aligned menu.
- Uses balanced Investigation and Monitoring work areas on wide terminals, with System actions separated clearly below.
- Collapses cleanly to medium and narrow layouts without horizontal overflow.
- Moves version and readiness status into the header hierarchy and keeps the AegisLog identity visible without dominating the screen.
- Removes the duplicate fake `SELECT >` prompt so the real shell prompt is the only authoritative input path.
- Uses ASCII-safe structural chrome and adds explicit Windows rendering regression coverage.
- Adds layout tests for common terminal widths, wide-screen utilization, narrow-screen fit, footer behavior, and Windows-safe output.
- Preserves the v1.9 streaming-correlation, authentication-parser, timestamp-window, IPv4/IPv6, and synthetic regression hardening without changing detection semantics.
- Keeps AI Analyst removed from the public product surface; AegisLog continues to rely on deterministic detection, correlation, and read-only investigation workflows.

## Product behavior

AegisLog remains terminal-first, local-first, read-only by default, and deterministic for detection and correlation. v2.0.0 changes the operator experience and visual composition of Mission Control; it does not introduce a new detection-rule family or weaken the evidence-first security model.

## Validation

The release candidate is gated by CI across supported Python versions, security checks, package build validation, runtime/validation/build lock audits, the maintained synthetic detection regression evaluation, and a Windows single-executable build and smoke test. Publication remains fail-closed and refuses to reuse an existing v2.0.0 tag or release.

## Windows

The GitHub release publishes an unsigned `AegisLog.exe` and matching SHA-256 checksum file. Windows SmartScreen may warn because the executable is not code-signed.

## Detection evidence note

The maintained synthetic corpus remains regression evidence, not an independent real-world benchmark. Its zero-FP/zero-FN result applies only to the labeled fixtures in the repository and does not establish deployment-specific false-positive rates, adversarial robustness, or general detection effectiveness.
