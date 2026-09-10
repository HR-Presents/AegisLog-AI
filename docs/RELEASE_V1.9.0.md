# AegisLog v1.9.0

AegisLog v1.9.0 is a correctness and release-hardening update for the deterministic, local-first defensive log investigation workflow.

## Highlights

- Makes streaming authentication correlation independent of chunk boundaries by preserving one bounded correlation state across the full stream.
- Adds explicit RFC3164 year-hint support to streaming analysis so full-file and streaming paths use the same timestamp context.
- Improves authentication parsing for RFC3164 syslog hosts and validated IPv4/IPv6 source addresses.
- Prevents destination-only addresses from being treated as authentication sources.
- Adds regression coverage for out-of-order authentication events, exact correlation-window boundaries, expired events, and missing-timestamp fallback behavior.
- Expands the maintained synthetic detection corpus from 12 to 18 labeled cases, including IPv6, structured-source, destination-only, distinct-source, and out-of-order authentication scenarios.
- Keeps the synthetic regression gate fail-closed at 100% precision, 100% recall, 100% exact-case accuracy, zero false positives, and zero false negatives for the maintained fixtures.
- Preserves the responsive, Windows-console-safe terminal identity introduced in v1.8.0.
- AI Analyst remains removed from the public product surface; AegisLog continues to rely on deterministic detection, correlation, and read-only investigation workflows.

## Product behavior

AegisLog remains terminal-first, local-first, read-only by default, and deterministic for detection and correlation. This release focuses on correlation correctness, authentication accuracy, and regression evidence rather than adding new detection-rule families.

## Validation

The release candidate is gated by CI, security checks, package build validation, runtime/validation/build lock audits, synthetic detection regression evaluation, and a Windows single-executable smoke test. Release publication remains fail-closed and refuses to reuse an existing v1.9.0 tag or release.

## Windows

The GitHub release publishes an unsigned `AegisLog.exe` and matching SHA-256 checksum file. Windows SmartScreen may warn because the executable is not code-signed.

## Detection evidence note

The maintained synthetic corpus is regression evidence, not an independent real-world benchmark. Its zero-FP/zero-FN result applies only to the labeled fixtures in the repository and does not establish deployment-specific false-positive rates, adversarial robustness, or general detection effectiveness.
