# AegisLog v2.1.0

AegisLog v2.1.0 is a reliability and evaluation-evidence hardening release for the terminal-first, local-first, read-only defensive investigation platform.

## Highlights

- Added deterministic fuzz-style regression coverage for malformed input, randomized streaming chunk boundaries, authentication event reordering, and bounded authentication-source floods.
- Strengthened external detection evidence with schema v2, including explicit source types, collection period, sampling method, known exclusions, class balance, expected-category counts, per-category metrics, and confidence intervals.
- Added a broader representative synthetic benchmark corpus with benign controls, near-miss cases, authentication variants, and coverage across authentication, audit, error, network, privilege, service, and web categories.
- Kept release-readiness and development-state documentation synchronized before publication.

## Detection and runtime semantics

This release does not intentionally change AegisLog detection, parsing, streaming, authentication, CLI investigation, live-monitoring, or read-only security semantics. The v2.0 Mission Control experience and the v1.9 correctness hardening remain in place.

AI Analyst and remote-provider workflows remain outside the supported public product surface. Deterministic local investigation remains authoritative.

## Evaluation scope

The checked-in benchmark datasets are synthetic regression fixtures. Their exact 1.0 precision, recall, and case-level accuracy gates are intended to catch deterministic regressions in known labeled cases; they are not evidence of deployment-specific or general real-world detection effectiveness.

External evidence must be authorized, sanitized, independently labeled, and accompanied by truthful provenance. AegisLog v2.1.0 does not fabricate or imply such evidence where none exists.

## Distribution

The release workflow builds a standalone Windows `AegisLog.exe`, generates a matching SHA-256 checksum, verifies the artifact before publication, and publishes the executable and checksum as GitHub Release assets.

The Windows executable is not Authenticode-signed in this release. Windows SmartScreen or antivirus reputation warnings may therefore occur even when the published SHA-256 checksum matches.

## Verification

Before publication, the release candidate must pass the repository's required CI, security, package-build, Windows executable, and dependency-lock checks on the exact release-preparation head. The guarded release workflow then repeats release-candidate validation, including both maintained synthetic detection corpora, before building and publishing artifacts.
