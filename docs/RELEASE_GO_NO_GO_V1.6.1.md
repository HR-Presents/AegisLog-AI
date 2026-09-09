# AegisLog AI v1.6.1 release go/no-go

Status: **READY FOR FINAL RELEASE VALIDATION**

This document records current release-readiness state. It does not itself publish or tag a release.

## Current project state

- Published stable release remains `v1.6.0` until v1.6.1 is actually published.
- v1.6.1 code, UI, documentation, packaging, security checks, and automated validation are prepared for the guarded release workflow.
- External real-world benchmarking is valuable future evaluation work, but it is **not a release gate** and no real-world detection percentage is claimed.

## Release gates

- [x] v1.6.1 version metadata is aligned.
- [x] Dedicated guarded v1.6.1 release workflow exists.
- [x] Release workflow requires dispatch from `main` with exact confirmation `RELEASE-v1.6.1`.
- [x] Release workflow runs quality, security, packaging, checksum, provenance, and smoke-test gates.
- [x] Release workflow builds a one-file Windows `AegisLog.exe` and publishes only the executable plus checksum.
- [x] Synthetic detection fixtures remain regression tests, not claims of deployment effectiveness.
- [x] External-evaluation tooling remains available for future independently reviewed benchmarking.
- [x] Mandatory Windows Authenticode signing is not part of the current release gate.

## Evidence policy

AegisLog does not claim a universal real-world detection percentage. The synthetic labeled fixtures in the repository verify deterministic regression behavior only; they do not establish deployment-specific false-positive rates, prevalence, adversarial robustness, or production detection effectiveness.

If independently reviewed external evidence is produced later, it must retain truthful provenance, labeling, sanitization, reviewer, uncertainty, and evaluated-commit metadata. The existing external-evaluation tooling remains available for that purpose. Such research evidence is not required to ship v1.6.1.

## Remaining release action

The guarded `Release v1.6.1` workflow must be dispatched from the intended `main` commit with confirmation `RELEASE-v1.6.1`. Publication is appropriate only if all mandatory quality, security, packaging, Windows smoke, checksum, provenance, and immutability checks pass.

After publication, verify the public release target, exact asset set, SHA-256 checksum, provenance attestation, and clean-machine behavior.

## Decision

```text
READY FOR FINAL RELEASE VALIDATION
```

This status means the project no longer has an artificial external-benchmark blocker. It does **not** mean v1.6.1 has already been published, and it does not convert synthetic test results into real-world accuracy claims.
