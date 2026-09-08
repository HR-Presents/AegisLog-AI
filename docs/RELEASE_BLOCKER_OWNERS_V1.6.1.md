# AegisLog AI v1.6.1 — Release blocker owners

This file converts the remaining v1.6.1 release blockers into an owner-by-owner action list. It is intentionally fail-closed: completing one item does not authorize publication unless every release gate is satisfied on the exact release candidate commit.

## Current status

Production release status: **NO-GO**.

The PR branch has demonstrated a fully green seven-workflow validation on commit `1856a53c7d632cadce0049f0fb191e5e9e833bab`, including the Windows single-executable build. That validation remains PR evidence only. The actual release must be validated from the exact merged `main` candidate through the guarded `release-v1.6.1.yml` workflow.

## 1. PR owner / maintainers

**Owner:** PR author and repository maintainers.

Actions:

- complete review of PR #77;
- keep the PR Draft until review is genuinely complete;
- resolve any requested changes;
- merge only after approval and only when the release-supporting documentation and code are accepted;
- record the exact merged `main` commit SHA that will become the release candidate.

Blocker is closed when:

- PR #77 is approved and merged;
- the exact resulting `main` commit is known;
- no additional unreviewed commits are added before release validation.

## 2. External dataset owner

**Owner:** person or organization authorized to provide the external evaluation data.

Actions:

- provide a real external JSONL evaluation dataset;
- ensure it is minimized and sanitized before use;
- document source, sampling, and provenance;
- do not substitute repository synthetic fixtures for external data;
- do not commit production/customer telemetry merely to run the release evaluation.

Blocker is closed when:

- the external dataset exists in an approved working location;
- its provenance and sanitization are documented;
- the dataset is ready for independent labeling.

See `docs/EXTERNAL_EVIDENCE_SUBMISSION.md`.

## 3. Independent reviewer / labeler

**Owner:** reviewer who did not derive labels from AegisLog output.

Actions:

- assign the expected detection categories independently;
- document the labeling procedure;
- provide the reviewer identity and reviewer role used for release evidence;
- confirm independent labeling and sanitization truthfully;
- review the generated evidence for accuracy.

Blocker is closed when:

- the required reviewer metadata is available;
- the labels are independently produced;
- the reviewer has approved the resulting evidence record.

## 4. Release evidence operator

**Owner:** release engineer or maintainer preparing the exact candidate.

Actions:

- wait until the exact merged `main` release candidate SHA is known;
- generate `evaluation/external-release-evidence.json` using `tools/build_external_evidence.py`;
- bind the evidence to that exact lowercase 40-character commit SHA;
- verify the recorded dataset SHA-256;
- verify the evidence records provenance, labeling procedure, reviewer metadata, independent labeling, sanitization, metrics, uncertainty, and limitations;
- do not reuse evidence generated for a different commit.

Blocker is closed when:

- `evaluation/external-release-evidence.json` exists;
- its `evaluated_commit` equals the exact release candidate SHA;
- its metadata is genuine and reviewed.

## 5. Organization administrator / signing owner

**Owner:** authorized administrator controlling code-signing material.

Actions:

- provision or confirm these repository-level release settings without exposing their values:
  - secret `WINDOWS_SIGNING_PFX_BASE64`;
  - secret `WINDOWS_SIGNING_PFX_PASSWORD`;
  - secret `WINDOWS_SIGNING_CERT_THUMBPRINT`;
  - variable `WINDOWS_SIGNING_TIMESTAMP_URL`;
- ensure the certificate contains a Code Signing EKU and private key;
- ensure the configured thumbprint is the approved release signer;
- ensure the timestamp endpoint is HTTPS and suitable for RFC3161 timestamping;
- keep private signing material out of the repository, issues, PR comments, chat, and logs.

Blocker is closed when:

- an authorized admin confirms the four required settings are correctly provisioned;
- the approved certificate identity and timestamp policy are documented operationally without leaking secrets.

See `docs/SIGNING_READINESS_V1.6.1.md`.

## 6. Release operator

**Owner:** maintainer authorized to publish releases.

Actions after all previous blockers are closed:

- confirm the release candidate is the intended exact commit on `main`;
- confirm `v1.6.1` tag and GitHub Release still do not exist;
- dispatch `.github/workflows/release-v1.6.1.yml` from `main`;
- enter the exact confirmation `RELEASE-v1.6.1`;
- do not bypass a failed preflight, test, audit, signing, checksum, attestation, or smoke-test gate;
- verify that the workflow publishes exactly:
  - `AegisLog.exe`;
  - `AegisLog.exe.sha256`.

Blocker is closed when:

- the guarded release workflow succeeds end-to-end on the exact candidate;
- the GitHub Release is published from that commit;
- both permanent release assets are present.

## 7. Post-release verifier

**Owner:** maintainer or independent verifier who can test the published assets.

Actions:

- download `AegisLog.exe` from the published GitHub Release, not from a temporary Actions artifact;
- download `AegisLog.exe.sha256`;
- verify the SHA-256 checksum;
- verify the Authenticode signature, expected signer thumbprint, and timestamp;
- perform a clean-machine smoke test of core commands;
- record any release-specific screenshot provenance using the published release asset if stable screenshots are added.

Blocker is closed when:

- checksum verification passes;
- Authenticode and timestamp verification pass;
- clean-install smoke testing passes;
- no critical release regression is found.

## Required order

1. Finish PR review.
2. Merge PR #77.
3. Freeze the exact `main` release candidate SHA.
4. Complete real external dataset labeling and evidence generation for that SHA.
5. Confirm signing configuration.
6. Run the guarded v1.6.1 release workflow from `main`.
7. Verify the published GitHub Release assets independently.

Do not reverse this order by generating final evidence for a moving branch, publishing unsigned binaries, treating a PR artifact as a release asset, or releasing before review and merge.
