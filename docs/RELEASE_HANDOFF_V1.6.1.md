# AegisLog AI v1.6.1 — Release Handoff

Use this handoff only after reading the v1.6.1 release checklist, go/no-go record, blocker-owner list, external-evidence guide, and signing-readiness guide. It is an operational handoff, not authorization to bypass any release gate.

## Current PR evidence point

At the time this handoff was prepared, PR #77 (`fix/polished-responsive-home` -> `main`) had an exact fully validated PR head:

- Commit: `eced0a47acc4270a4b0ef6a60e68e97c5639c7f9`
- PR workflows: 7/7 successful
- Windows workflow: `Windows single executable #420`
- Temporary validation artifact: `AegisLog-Windows-Single-EXE`
- Artifact ID: `10072272475`
- Artifact digest: `sha256:92e8062ef257d74eaa514c07cc79f296822093a65d034593440f1bec4f4c23b5`

This is PR validation evidence only. It is not the v1.6.1 production release binary. Any later commit requires its own exact-head validation before it can replace this evidence point.

## Handoff to PR maintainer

Please complete the normal review of PR #77. Do not merge merely because CI is green: review the code, documentation, security implications, and unresolved discussion first.

Before merge, confirm:

- required review/approval policy is satisfied;
- required checks for the exact head are successful;
- no unresolved blocking review comments remain;
- the PR is intentionally taken out of Draft only when the team considers it review-complete;
- the merge target is `main`;
- no release tag or GitHub Release is created as part of PR review.

After the approved merge, record the exact resulting `main` commit SHA. Do not assume it equals the PR head: the merge strategy may create a different commit.

## Handoff to external dataset owner

Provide a real, authorized, sanitized external evaluation dataset. Do not use repository synthetic fixtures as external evidence and do not copy AegisLog output into the ground-truth labels.

Provide enough provenance to explain the source, sampling method/period, relevant environment or source types, sanitization method, authorization/data-handling basis, class balance where known, and material limitations.

Do not commit sensitive raw telemetry, credentials, secrets, customer identifiers, or unnecessary personal information merely to produce release evidence.

## Handoff to independent reviewer

Independently label the external dataset without using AegisLog's detections as the source of truth. Record:

- genuine reviewer identity;
- reviewer role;
- labeling procedure;
- category/label definitions used;
- disagreement/adjudication procedure if applicable;
- confirmation that labeling was independent of AegisLog output.

If independence cannot truthfully be confirmed, stop. The dataset must not be represented as independently labeled external release evidence.

## Handoff to evidence operator

Only after the approved PR has been merged and the exact release-candidate `main` SHA is fixed, generate `evaluation/external-release-evidence.json` using `tools/build_external_evidence.py` and the real reviewed external dataset.

Use the exact 40-character lowercase candidate SHA and genuine metadata. The command must include both explicit assertions:

```text
--independent-labeling --sanitized
```

Review the generated evidence before release. Confirm that `evaluated_commit` equals the exact candidate SHA and `dataset_sha256` corresponds to the reviewed dataset. Do not edit metrics by hand and do not fabricate provenance, reviewer information, or labels.

The generator intentionally refuses to overwrite an existing evidence file. Resolve any existing-file situation deliberately rather than weakening that protection.

## Handoff to signing administrator

In GitHub repository settings, confirm the release environment has valid values for:

- `WINDOWS_SIGNING_PFX_BASE64`
- `WINDOWS_SIGNING_PFX_PASSWORD`
- `WINDOWS_SIGNING_CERT_THUMBPRINT`
- `WINDOWS_SIGNING_TIMESTAMP_URL`

Do not paste secret values into issues, pull requests, logs, documentation, chat, or source files.

Confirm the certificate is valid for Windows code signing, contains the expected private key, matches the configured thumbprint, and is appropriate for the intended publisher. Confirm the timestamp URL is the intended HTTPS RFC3161 service.

## Handoff to release operator

Do not run the v1.6.1 release workflow until all prior gates are closed.

Immediately before dispatch:

1. Work from the exact intended `main` candidate commit.
2. Confirm version metadata is `1.6.1`.
3. Confirm genuine external release evidence is present and bound to that exact candidate.
4. Confirm signing configuration has been checked by an authorized administrator.
5. Confirm no existing `v1.6.1` tag or GitHub Release exists.
6. Confirm the release notes/checklists still describe the intended release.
7. Confirm no unreviewed change has moved `main` since the evidence was generated.

Then dispatch `.github/workflows/release-v1.6.1.yml` from `main` with the exact confirmation required by the workflow:

```text
RELEASE-v1.6.1
```

Do not weaken or bypass a failing preflight, quality, evaluation, signing, timestamp, checksum, provenance, or immutability gate. A failed gate means NO-GO until its cause is understood and corrected.

The production release must come from the guarded release workflow. The PR Actions artifact above is temporary validation evidence and must not be relabeled as the permanent customer download.

## Handoff to post-release verifier

After successful publication, independently verify the GitHub Release before announcing it broadly:

- tag and release target the intended candidate commit;
- exactly the intended permanent assets are present: `AegisLog.exe` and `AegisLog.exe.sha256`;
- the published executable matches the published SHA-256 checksum;
- Authenticode signature is valid;
- signer identity/certificate is the intended publisher;
- trusted timestamp is present and valid;
- clean-machine smoke testing succeeds for the documented workflows;
- no unexpected network, write, or privilege behavior is observed relative to the documented local-first/read-only design.

Stable screenshots must be captured from this exact published release executable and tied to its checksum. Do not promote a PR-preview screenshot to stable-release evidence merely because the PR later merged.

## Stop conditions

Stop the release and keep status NO-GO if any of the following is true:

- PR review/approval is incomplete;
- the exact candidate SHA is ambiguous or changed after evidence generation;
- external evidence is synthetic, circularly labeled, unsanitized, unauthorized, fabricated, or bound to another commit;
- signing configuration is missing or cannot be independently confirmed by an authorized administrator;
- a release/tag collision exists;
- any required workflow gate fails;
- Authenticode or timestamp verification fails;
- checksum or provenance verification fails;
- the release asset set differs from the expected set;
- a material security or correctness issue is discovered during final verification.

## Copy/paste maintainer handoff

> PR #77 has a fully validated PR evidence point at `eced0a47acc4270a4b0ef6a60e68e97c5639c7f9` with 7/7 PR workflows successful, including Windows single executable #420. Please complete normal code/review-policy checks before taking the PR out of Draft or merging. After an approved merge, record the exact resulting `main` SHA; do not assume it is the PR-head SHA. No v1.6.1 release should be dispatched until genuine external evidence is generated for that exact candidate and signing configuration is confirmed by an authorized admin.

## Copy/paste release-operator handoff

> Do not release from the PR branch or its temporary Actions artifact. Once PR #77 is approved and merged, freeze the exact `main` candidate SHA, generate genuine sanitized independently labeled external evidence for that exact SHA, confirm the Windows signing configuration, and re-check that `v1.6.1` does not already exist. Only then dispatch the guarded `.github/workflows/release-v1.6.1.yml` workflow from `main` using the workflow's exact confirmation. Treat any failed preflight, evaluation, signing, timestamp, checksum, provenance, or immutability gate as NO-GO; do not bypass it.
