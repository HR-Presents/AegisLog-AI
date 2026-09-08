# AegisLog AI v1.6.1 — Release blocker owners

This file converts the remaining v1.6.1 release blockers into an owner-by-owner action list. It is intentionally fail-closed: completing one item does not authorize publication unless every release gate is satisfied on the exact release commit.

## Current status

Production release status: **NO-GO**.

The PR branch has demonstrated fully green seven-workflow validation on commit `dcde3f5d147715a952e743fe3216eca6efd8344c`, including Windows single executable #425 and matching temporary artifact `10073054699` (`sha256:b87c7ff06eecdb37e6c8765f57cad58c107d04caca88efeffcbd820513866db7`). This remains PR evidence only.

## 1. PR owner / maintainers

Complete review of PR #77, keep it Draft until review is genuinely complete, resolve requested changes, merge only after approval, and record the exact resulting `main` commit SHA.

Blocker closes when PR #77 is approved and merged and the exact merged `main` code SHA is known. That SHA becomes the **evaluated code commit**.

## 2. External dataset owner

Provide a real external JSONL evaluation dataset, minimize/sanitize it before use, document source/sampling/provenance, and do not substitute repository synthetic fixtures or commit sensitive production/customer telemetry.

Blocker closes when an authorized sanitized dataset and its provenance are available for independent labeling. See `docs/EXTERNAL_EVIDENCE_SUBMISSION.md`.

## 3. Independent reviewer / labeler

Assign expected detection categories independently of AegisLog output, document the labeling procedure, provide genuine reviewer identity/role, and confirm independent labeling and sanitization truthfully.

Blocker closes when reviewer metadata and independently produced labels are complete and reviewed.

## 4. Release evidence operator

After the exact merged `main` code SHA is fixed:

- generate `evaluation/external-release-evidence.json` with `tools/build_external_evidence.py`;
- set `evaluated_commit` to that exact lowercase 40-character code SHA;
- verify dataset SHA-256, provenance, labeling procedure, reviewer metadata, metrics, uncertainty, and limitations;
- commit **only** `evaluation/external-release-evidence.json` as the immediate direct child of the evaluated code commit;
- do not include code, workflow, documentation, dependency, or any other path in the evidence commit;
- record the evidence-only child SHA as the release commit.

Blocker closes when the evidence file is genuine and reviewed and the release commit is a single-parent direct child of `evaluated_commit` whose parent-to-child diff is exactly `evaluation/external-release-evidence.json`.

The release preflight rejects stale evidence, arbitrary ancestor evidence, merge commits, and evidence commits containing any additional changed path.

## 5. Organization administrator / signing owner

Provision or confirm without exposing values:

- secret `WINDOWS_SIGNING_PFX_BASE64`;
- secret `WINDOWS_SIGNING_PFX_PASSWORD`;
- secret `WINDOWS_SIGNING_CERT_THUMBPRINT`;
- variable `WINDOWS_SIGNING_TIMESTAMP_URL`.

Ensure the certificate has Code Signing EKU and private key, the thumbprint is the approved signer, and the timestamp endpoint is credential-free HTTPS/RFC3161. Keep private material out of the repository, issues, PR comments, chat, and logs.

Blocker closes when an authorized administrator confirms all required signing settings and release identity are correctly provisioned. See `docs/SIGNING_READINESS_V1.6.1.md`.

## 6. Release operator

After all previous blockers close:

- confirm current `main` is exactly the intended evidence-only release commit;
- confirm its sole parent equals evidence field `evaluated_commit`;
- confirm the parent-to-release diff is exactly `evaluation/external-release-evidence.json`;
- confirm no later unreviewed commit moved `main`;
- confirm `v1.6.1` tag and GitHub Release do not exist;
- dispatch `.github/workflows/release-v1.6.1.yml` from `main` with `RELEASE-v1.6.1`;
- do not bypass preflight, test, audit, signing, checksum, attestation, or smoke-test failures;
- verify the workflow publishes exactly `AegisLog.exe` and `AegisLog.exe.sha256`.

Blocker closes when the guarded workflow succeeds end-to-end on that exact evidence-only release commit and the GitHub Release is published with both permanent assets.

## 7. Post-release verifier

Download the assets from the published GitHub Release, verify SHA-256, Authenticode signer/thumbprint/timestamp, clean-machine smoke behavior, release target, and exact asset set. Stable screenshots, if added, must come from the exact published release executable.

Blocker closes when checksum, signing/timestamp, clean-install smoke tests, and release-target verification all pass without a critical regression.

## Required order

1. Finish PR review.
2. Merge PR #77 and record the exact merged `main` code SHA.
3. Freeze that SHA as the evaluated commit.
4. Complete real external dataset labeling and generate evidence bound to that evaluated commit.
5. Commit only `evaluation/external-release-evidence.json` as the immediate direct child; this creates the release commit.
6. Confirm signing configuration and that `main` still points exactly to the evidence-only release commit.
7. Run the guarded v1.6.1 release workflow from that commit.
8. Independently verify the published GitHub Release assets.

Do not reverse this order by generating final evidence for a moving branch, adding unrelated changes to the evidence commit, publishing unsigned binaries, treating a PR artifact as a release asset, or releasing before review and merge.
