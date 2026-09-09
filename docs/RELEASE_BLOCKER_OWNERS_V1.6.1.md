# AegisLog AI v1.6.1 — Release blocker owners

This file converts the remaining v1.6.1 release blockers into an owner-by-owner action list. Completing one item does not authorize publication unless every mandatory release gate is satisfied on the exact release commit.

## Current status

Production release status: **NO-GO**.

The project has moved beyond the original PR #77 candidate through later validated UI and documentation work. The final intended v1.6.1 evaluated code commit has not yet been frozen, and qualifying external evidence has not yet been established for it.

Mandatory Windows Authenticode signing has been removed from the current v1.6.1 release path.

## 1. Candidate owner / maintainers

Select the exact `main` commit intended for v1.6.1 and record it as the **evaluated code commit**.

Blocker closes when the final candidate is frozen and the required CI, security, package, Windows-build, and lock-audit validation is acceptable for that exact commit.

## 2. External dataset owner

Provide a real external evaluation dataset, minimize and sanitize it before use, document source/sampling/provenance, and do not substitute repository synthetic fixtures or commit sensitive production/customer telemetry.

Blocker closes when an authorized sanitized dataset and its provenance are available for independent labeling. See `docs/EXTERNAL_EVIDENCE_SUBMISSION.md`.

## 3. Independent reviewer / labeler

Assign expected detection categories independently of AegisLog output, document the labeling procedure, provide genuine reviewer identity/role, and confirm independent labeling and sanitization truthfully.

Blocker closes when reviewer metadata and independently produced labels are complete and reviewed.

## 4. Release evidence operator

After the exact evaluated code commit is frozen:

- generate `evaluation/external-release-evidence.json` with `tools/build_external_evidence.py`;
- set `evaluated_commit` to that exact code SHA;
- verify dataset SHA-256, provenance, labeling procedure, reviewer metadata, metrics, uncertainty, and limitations;
- commit **only** `evaluation/external-release-evidence.json` as the immediate direct child of the evaluated code commit;
- do not include code, workflow, documentation, dependency, or any other path in the evidence commit;
- record the evidence-only child SHA as the release commit.

Blocker closes when the evidence is genuine and reviewed and the release commit is a single-parent direct child of `evaluated_commit` whose parent-to-child diff is exactly `evaluation/external-release-evidence.json`.

## 5. Release operator

After the previous blockers close:

- confirm current `main` is exactly the intended evidence-only release commit;
- confirm its sole parent equals evidence field `evaluated_commit`;
- confirm the parent-to-release diff is exactly `evaluation/external-release-evidence.json`;
- confirm no later unreviewed commit moved `main`;
- confirm `v1.6.1` tag and GitHub Release do not exist;
- dispatch `.github/workflows/release-v1.6.1.yml` from `main` with `RELEASE-v1.6.1`;
- do not bypass preflight, test, audit, checksum, attestation, or smoke-test failures;
- verify the workflow publishes exactly `AegisLog.exe` and `AegisLog.exe.sha256`.

Blocker closes when the guarded workflow succeeds end-to-end on that exact evidence-only release commit and the public GitHub Release is published with both permanent assets.

The current workflow intentionally publishes an **unsigned** Windows executable. Signing may be added later but is not a current blocker.

## 6. Post-release verifier

Download the assets from the published GitHub Release, verify SHA-256, clean-machine smoke behavior, release target, and exact asset set. Confirm remote AI remains disabled by default and local core analysis works without network access.

Stable screenshots, if added, must come from the exact published release executable.

Blocker closes when checksum, clean-install smoke tests, release-target verification, and the documented privacy/default-network posture all pass without a critical regression.

## Required order

1. Freeze the exact final v1.6.1 evaluated code commit.
2. Complete real external dataset labeling and generate evidence bound to that commit.
3. Commit only `evaluation/external-release-evidence.json` as the immediate direct child; this creates the release commit.
4. Confirm `main` still points exactly to that evidence-only release commit.
5. Run the guarded v1.6.1 release workflow from that commit.
6. Independently verify the published GitHub Release assets.

Do not generate final evidence for a moving branch, add unrelated changes to the evidence commit, treat a PR artifact as a release asset, fabricate review/evidence metadata, or claim publication before the GitHub Release actually exists.