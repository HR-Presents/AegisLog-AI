# AegisLog AI v1.6.1 Release Readiness Checklist

This checklist is the operator-facing gate for publishing the permanent GitHub Release assets for `v1.6.1`.

It is intentionally fail-closed. A checked item means the requirement has been verified with evidence; unchecked items are release blockers or pending operator actions.

## Candidate identity

AegisLog v1.6.1 uses two distinct commit identities:

- **Evaluated code commit:** exact reviewed `main` commit whose code is evaluated against the external dataset.
- **Evidence-only release commit:** immediate single-parent child of the evaluated code commit that changes exactly `evaluation/external-release-evidence.json`.

- [x] `pyproject.toml` declares version `1.6.1`.
- [x] `src/aegislog/__init__.py` declares `__version__ = "1.6.1"`.
- [x] The repository contains `docs/RELEASE_V1.6.1.md`.
- [ ] The reviewed change set has been merged to `main`.
- [ ] The exact evaluated code commit SHA on `main` has been recorded before evidence generation.
- [ ] The exact evidence-only release commit SHA has been recorded before workflow dispatch.

Evaluated code commit SHA:

```text
PENDING
```

Evidence-only release commit SHA:

```text
PENDING
```

## Pull request / review state

- [ ] PR #77 is no longer Draft.
- [ ] Required human review has completed.
- [ ] No unresolved blocking review threads remain.
- [ ] PR #77 has been merged into `main`.

Do not publish directly from the PR branch. The release workflow requires `refs/heads/main`.

## Exact evaluated-code validation

For the exact evaluated code commit on `main`, verify the required validation remains acceptable for release preparation. Historical green PR runs support review but do not identify the final merged code commit if the merge strategy changes its SHA.

- [ ] Exact evaluated code commit is recorded.
- [ ] No unreviewed code/workflow/dependency changes occur after it is frozen.
- [ ] Required CI/security/package/Windows/lock audits for the intended code are green or have been revalidated according to project policy.

The evidence-only release commit must contain no code changes, so its release workflow preflight binds it back to this evaluated code commit.

## External release evidence

Current status: **BLOCKED — genuine external evidence has not yet been produced for the final merged evaluated code commit.**

Before release:

- [ ] Obtain a real, sanitized, independently labeled external evaluation dataset.
- [ ] Keep underlying production/customer telemetry out of the repository unless explicitly authorized and safely sanitized.
- [ ] Generate `evaluation/external-release-evidence.json` using `tools/build_external_evidence.py` with `--evaluated-commit` set to the exact evaluated code commit SHA.
- [ ] Include real provenance, labeling procedure, reviewer metadata, `--independent-labeling`, and `--sanitized`.
- [ ] Verify `dataset_sha256`, metrics, confidence intervals, limitations, and reviewer metadata.
- [ ] Review the generated evidence for accuracy before it is committed.

Then create the release commit:

- [ ] Start from the exact evaluated code commit on `main`.
- [ ] Commit only `evaluation/external-release-evidence.json`.
- [ ] Confirm the new commit has exactly one parent and that parent is the evaluated code commit.
- [ ] Confirm no code, workflow, docs, dependencies, lockfiles, or other paths changed in the evidence-only commit.
- [ ] Record the resulting evidence-only release commit SHA.
- [ ] Confirm `tools/release_preflight.py` accepts the evidence manifest and commit binding.

Do not substitute fabricated reviewer metadata, synthetic-only evidence, placeholder provenance, or a manual checkbox for the required external evidence. Do not amend the evaluated code commit to include the evidence file and do not combine evidence with unrelated changes.

## Windows signing configuration

An authorized organization administrator must provision the real signing material outside the repository and chat systems:

- [ ] `WINDOWS_SIGNING_PFX_BASE64`
- [ ] `WINDOWS_SIGNING_PFX_PASSWORD`
- [ ] `WINDOWS_SIGNING_CERT_THUMBPRINT`
- [ ] `WINDOWS_SIGNING_TIMESTAMP_URL`

Additional checks:

- [ ] Timestamp URL uses HTTPS.
- [ ] Certificate thumbprint matches the approved release identity.
- [ ] Signing material is not committed to Git, release notes, issues, PR comments, screenshots, or documentation.
- [ ] Authenticode verification succeeds and a timestamp is present.

## Release workflow guardrails

Workflow: `.github/workflows/release-v1.6.1.yml`

Before dispatch:

- [ ] `main` points to the exact evidence-only release commit.
- [ ] The evidence-only release commit is the direct single-parent child of the evaluated code commit.
- [ ] Its only changed path is `evaluation/external-release-evidence.json`.
- [ ] Use the exact workflow confirmation value `RELEASE-v1.6.1`.
- [ ] Confirm tag `v1.6.1` does not already exist.
- [ ] Confirm a GitHub Release named/tagged `v1.6.1` does not already exist.
- [ ] Confirm release preflight passes repository, ref, release SHA, evidence binding, tag, version, confirmation, signing, timestamp, and external-evidence checks.

The workflow must refuse publication if any of these checks fail.

## Build and publication requirements

The release workflow must:

- [ ] Build exactly one customer executable: `AegisLog.exe`.
- [ ] Run release smoke tests against the built executable.
- [ ] Sign `AegisLog.exe` with the approved release identity.
- [ ] Verify the Authenticode signer and timestamp.
- [ ] Generate `AegisLog.exe.sha256`.
- [ ] Verify the checksum before publication.
- [ ] Create build provenance attestation.
- [ ] Publish the executable and checksum as GitHub Release assets.

Permanent customer assets:

```text
AegisLog.exe
AegisLog.exe.sha256
```

GitHub Actions artifacts are temporary validation evidence. They are not the permanent customer download channel.

## Post-publication verification

After the GitHub Release is published:

- [ ] Confirm the release/tag targets the evidence-only release commit.
- [ ] Confirm that commit is correctly bound to the intended evaluated code commit.
- [ ] Download `AegisLog.exe` from the public `v1.6.1` GitHub Release page.
- [ ] Download `AegisLog.exe.sha256` from the same release.
- [ ] Verify the downloaded executable against the published checksum.
- [ ] Verify the Authenticode signature, signer identity, and timestamp on a clean Windows system.
- [ ] Run a clean-install smoke test from the published release asset, not from a CI artifact.
- [ ] Confirm `AegisLog.exe --version` reports `1.6.1`.
- [ ] Confirm the primary command surface opens successfully.
- [ ] Confirm `dashboard`, `incidents`, and `investigate` work with sanitized example data.
- [ ] Confirm the permanent release links in README/docs point to the published `v1.6.1` assets.
- [ ] Record the final public executable SHA-256 in the release notes or verification documentation.

## Screenshot / README promotion

- [ ] Real Windows screenshots are captured from the exact published `v1.6.1` executable if they will be labeled as stable-release screenshots.
- [ ] Screenshot source commit/release provenance is recorded.
- [ ] Screenshots contain no credentials, tokens, personal data, production logs, private hostnames, or customer information.
- [ ] README screenshot captions describe only behavior visible in the exact released build.
- [ ] README stable-release text is updated from `v1.6.0` to `v1.6.1` only after publication succeeds.

## Release decision

Release is authorized only when every mandatory item above is satisfied.

Current decision:

```text
NOT READY FOR PUBLICATION
Reason: PR is still Draft/unmerged, genuine external evidence is not yet available for the final evaluated code commit, and signing configuration still requires authorized administrator confirmation.
```
