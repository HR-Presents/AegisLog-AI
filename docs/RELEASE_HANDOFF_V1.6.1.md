# AegisLog AI v1.6.1 — Release Handoff

Use this handoff only after reading the v1.6.1 release checklist, go/no-go record, blocker-owner list, external-evidence guide, and signing-readiness guide. It is an operational handoff, not authorization to bypass any release gate.

## Current PR evidence point

PR #77 (`fix/polished-responsive-home` -> `main`) has an exact fully validated PR head:

- Commit: `dcde3f5d147715a952e743fe3216eca6efd8344c`
- PR workflows: 7/7 successful
- Windows workflow: `Windows single executable #425`
- Temporary validation artifact: `AegisLog-Windows-Single-EXE`
- Artifact ID: `10073054699`
- Artifact digest: `sha256:b87c7ff06eecdb37e6c8765f57cad58c107d04caca88efeffcbd820513866db7`

This is PR validation evidence only. It is not the v1.6.1 production release binary. Any later code or release-supporting commit requires its own exact-head validation before replacing this evidence point.

## Handoff to PR maintainer

Complete normal review of PR #77. Do not merge merely because CI is green. Review code, tests, documentation, security implications, and unresolved discussion first.

Before merge, confirm required review policy is satisfied, exact-head checks are successful, no blocking review comments remain, the PR is intentionally taken out of Draft only when review-complete, and the merge target is `main`. Do not create a release tag or GitHub Release as part of PR review.

After approved merge, record the exact resulting `main` SHA. Do not assume it equals the PR head; merge strategy may create a different commit. That merged commit becomes the **evaluated code commit** for external release evidence.

## Handoff to external dataset owner and independent reviewer

Provide a real, authorized, sanitized external evaluation dataset. Do not use repository synthetic fixtures as external evidence and do not derive labels from AegisLog output.

Document provenance, source/sampling, relevant environment or source types, sanitization, authorization/data handling, material limitations, reviewer identity/role, labeling procedure, category definitions, and adjudication where applicable. Do not commit sensitive raw telemetry, credentials, secrets, customer identifiers, or unnecessary personal information.

If independent labeling or sanitization cannot truthfully be confirmed, stop.

## Handoff to evidence operator

The release-evidence model intentionally separates the evaluated code commit from the final release commit to avoid an impossible self-referential Git SHA.

After the approved PR is merged and the exact evaluated `main` code SHA is fixed:

1. Run the real external evaluation against that exact code commit.
2. Generate `evaluation/external-release-evidence.json` with `tools/build_external_evidence.py` and set `evaluated_commit` to that exact code SHA.
3. Include the explicit assertions `--independent-labeling --sanitized` and genuine reviewer/provenance metadata.
4. Verify `dataset_sha256`, sample count, metrics, uncertainty, limitations, and reviewer metadata. Do not hand-edit metrics or fabricate provenance or labels.
5. Commit **only** `evaluation/external-release-evidence.json` as the immediate direct child of the evaluated code commit. No code, workflow, documentation, dependency, or other file may change in that evidence commit.
6. Record the resulting evidence-only child SHA. This child is the release commit that the guarded workflow must validate and publish.

`tools/release_preflight.py` fails closed unless the release commit is a single-parent direct child of `evaluated_commit` and the diff between them is exactly `evaluation/external-release-evidence.json`. Stale evidence, arbitrary ancestor evidence, merge commits, or evidence commits containing any additional changed path are rejected.

The generator intentionally refuses to overwrite an existing evidence file. Resolve existing-file situations deliberately rather than weakening that protection.

## Handoff to signing administrator

In GitHub repository settings, confirm valid values are provisioned for:

- `WINDOWS_SIGNING_PFX_BASE64`
- `WINDOWS_SIGNING_PFX_PASSWORD`
- `WINDOWS_SIGNING_CERT_THUMBPRINT`
- `WINDOWS_SIGNING_TIMESTAMP_URL`

Do not paste secret values into issues, pull requests, logs, documentation, chat, or source files. Confirm the certificate is valid for Windows code signing, contains the expected private key, matches the configured thumbprint, and is appropriate for the intended publisher. Confirm the timestamp URL is the intended credential-free HTTPS RFC3161 service.

## Handoff to release operator

Do not run the v1.6.1 release workflow until all prior gates are closed.

Immediately before dispatch:

1. Confirm the current `main` commit is the intended **evidence-only release commit**.
2. Confirm it has exactly one parent and that parent SHA equals `evaluation/external-release-evidence.json` field `evaluated_commit`.
3. Confirm the parent-to-release diff contains exactly `evaluation/external-release-evidence.json` and no other path.
4. Confirm version metadata remains `1.6.1` in the evaluated parent/release tree.
5. Confirm genuine external evidence, signing configuration, release notes, and checklists are complete.
6. Confirm no existing `v1.6.1` tag or GitHub Release exists.
7. Confirm no later unreviewed commit has moved `main` beyond the evidence-only release commit.

Then dispatch `.github/workflows/release-v1.6.1.yml` from `main` with:

```text
RELEASE-v1.6.1
```

Do not weaken or bypass a failing preflight, quality, evaluation, signing, timestamp, checksum, provenance, or immutability gate. A failed gate means NO-GO until its cause is understood and corrected.

The production release must come from the guarded release workflow. PR Actions artifacts are temporary validation evidence and must not be relabeled as permanent customer downloads.

## Handoff to post-release verifier

After successful publication, independently verify the release targets the intended evidence-only release commit, contains exactly `AegisLog.exe` and `AegisLog.exe.sha256`, passes checksum verification, has valid Authenticode signer identity and trusted timestamp, and passes clean-machine smoke testing without unexpected network/write/privilege behavior relative to the documented design.

Stable screenshots must be captured from the exact published release executable and tied to its checksum. Do not promote a PR-preview screenshot to stable-release evidence merely because the PR later merged.

## Stop conditions

Keep the release NO-GO if review is incomplete; the evaluated code SHA or release SHA is ambiguous; the release commit is not a direct evidence-only child; external evidence is synthetic, circularly labeled, unsanitized, unauthorized, fabricated, or stale; signing configuration cannot be confirmed; a tag/release collision exists; any required workflow gate fails; signature/timestamp/checksum/provenance verification fails; or a material security/correctness issue is discovered.

## Copy/paste maintainer handoff

> PR #77 has a fully validated PR evidence point at `dcde3f5d147715a952e743fe3216eca6efd8344c` with 7/7 PR workflows successful, including Windows single executable #425. Complete normal review before taking the PR out of Draft or merging. After approved merge, record the exact resulting `main` code SHA; that is the evaluated commit for genuine external evidence. No release is authorized by this handoff.

## Copy/paste release-operator handoff

> After PR #77 is approved and merged, freeze the exact merged `main` code SHA and generate genuine sanitized independently labeled external evidence for that SHA. Commit only `evaluation/external-release-evidence.json` as its immediate direct child; that evidence-only child becomes the release commit. Confirm signing configuration and absence of an existing `v1.6.1` tag/release, then dispatch the guarded workflow from that exact `main` commit using `RELEASE-v1.6.1`. Treat any failed preflight, evaluation, signing, timestamp, checksum, provenance, or immutability gate as NO-GO.
