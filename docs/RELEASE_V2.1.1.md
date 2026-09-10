# AegisLog v2.1.1

AegisLog v2.1.1 is a focused Windows terminal UI polish patch built from real rendered output.

## What changed

- Mission Control no longer uses the spreadsheet-style `INV / ACTION / PURPOSE` presentation.
- Wide Windows terminals now use a deliberate bounded composition instead of stretching the dashboard across the available width.
- Investigation and monitoring actions are presented as separate operator work areas with shorter descriptions and clearer hierarchy.
- System actions are compressed into a compact command row and the navigation footer is simplified.
- Version/readiness status remains anchored to the product identity while preserving ASCII/cp1252-safe output.
- Narrow terminals retain a compact fallback without losing supported actions.

## What did not change

This patch does not change detection, parsing, streaming, authentication, incident correlation, monitoring semantics, evidence handling, or the local-first/read-only security model.

AI Analyst remains removed from the public product surface. Deterministic investigation commands remain authoritative.

## Windows executable

The release workflow produces a single-file `AegisLog.exe` and `AegisLog.exe.sha256`, verifies the checksum before publication, and emits build provenance attestation for the executable.

The Windows executable is **not Authenticode-signed**. Users should verify the published SHA-256 checksum and GitHub release provenance before use.

## Validation scope

Release publication is gated on the maintained CI, security checks, locked dependency audits, package build, Windows single-executable build, synthetic detection regression gates, and release smoke tests.

Synthetic evaluation remains regression evidence only and is not a claim of real-world detection effectiveness.
