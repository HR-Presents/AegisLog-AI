# AegisLog v2.0.1

AegisLog v2.0.1 is a public-surface consistency patch for the v2 line. It carries the v2.0.0 terminal redesign forward unchanged while aligning the supported CLI, customer bundle, README examples, and current-status documentation with the AegisLog product identity.

## Highlights

- Removes stale `AegisLog AI` branding from the supported CLI version/help surface and customer bundle launchers/installers.
- Aligns the README Mission Control example with the v2.0.x terminal layout and removes the obsolete duplicate `SELECT` prompt from the documented flow.
- Updates the documentation index, project status, and roadmap so they no longer present v1.6.0 as the current release line.
- Adds regression coverage that locks the current public branding, version output, README terminal example, and release-status documentation.
- Preserves historical release notes and workflows where old names are part of the historical record.

## Product behavior

This patch does not change detection semantics, streaming correlation, authentication parsing, timestamp windows, incident correlation, or read-only host behavior. The deterministic local engine from v2.0.0 remains unchanged.

AI Analyst and remote-provider workflows remain outside the supported public product surface. AegisLog continues to rely on deterministic detection, correlation, and evidence-led investigation.

## Validation

The release candidate remains gated by CI across supported Python versions, security checks, package build validation, runtime/validation/build lock audits, the maintained synthetic detection regression evaluation, and the Windows single-executable build and smoke tests.

## Windows

The GitHub release publishes an unsigned `AegisLog.exe` and matching SHA-256 checksum file. Windows SmartScreen or endpoint-security reputation warnings may appear because the executable is not code-signed.

## Detection evidence note

The maintained synthetic corpus remains regression evidence, not an independent real-world benchmark. Its zero-FP/zero-FN result applies only to the labeled fixtures in the repository and does not establish deployment-specific false-positive rates, adversarial robustness, or general detection effectiveness.
