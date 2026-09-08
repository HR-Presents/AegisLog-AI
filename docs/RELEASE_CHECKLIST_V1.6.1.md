# AegisLog AI v1.6.1 Release Readiness Checklist

This checklist is the operator-facing gate for publishing the permanent GitHub Release assets for `v1.6.1`.

It is intentionally fail-closed. A checked item means the requirement has been verified with evidence; unchecked items are release blockers or pending operator actions.

## Candidate identity

- [x] `pyproject.toml` declares version `1.6.1`.
- [x] `src/aegislog/__init__.py` declares `__version__ = "1.6.1"`.
- [x] The repository contains `docs/RELEASE_V1.6.1.md`.
- [ ] The exact reviewed release candidate has been merged to `main`.
- [ ] The final release candidate commit SHA on `main` has been recorded here before dispatch.

Final candidate SHA:

```text
PENDING
```

## Pull request / review state

- [ ] PR #77 is no longer Draft.
- [ ] Required human review has completed.
- [ ] No unresolved blocking review threads remain.
- [ ] PR #77 has been merged into `main`.

Do not publish directly from the PR branch. The release workflow itself requires `refs/heads/main`.

## Exact-candidate CI gates

For the final candidate commit on `main`, verify all required workflows are green for that exact SHA:

- [ ] CI
- [ ] Security checks
- [ ] Package build
- [ ] Windows single executable
- [ ] Runtime lock audit
- [ ] Build toolchain lock audit
- [ ] Validation toolchain lock audit

Historical green PR runs may support review, but they do not replace exact-candidate release evidence after merge.

## External release evidence

Current status: **BLOCKED — `evaluation/external-release-evidence.json` is not present on the PR branch.**

Before release:

- [ ] Obtain a real, sanitized, independently labeled external evaluation dataset.
- [ ] Keep underlying production/customer telemetry out of the repository unless explicitly authorized and safely sanitized.
- [ ] Generate `evaluation/external-release-evidence.json` using `tools/build_external_evidence.py`.
- [ ] Include real provenance, labeling procedure, reviewer metadata, `--independent-labeling`, and `--sanitized`.
- [ ] Ensure the evidence identifies the exact final release candidate commit SHA.
- [ ] Review the generated evidence for accuracy before dispatch.
- [ ] Confirm release preflight accepts the evidence file.

Do not substitute fabricated reviewer metadata, synthetic-only evidence, placeholder provenance, or a manual checkbox for the required external evidence.

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

- [ ] Run from `main` only.
- [ ] Use the exact workflow confirmation value `RELEASE-v1.6.1`.
- [ ] Confirm tag `v1.6.1` does not already exist.
- [ ] Confirm a GitHub Release named/tagged `v1.6.1` does not already exist.
- [ ] Confirm release preflight passes repository, ref, SHA, tag, version, confirmation, signing, timestamp, and external-evidence checks.

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
Reason: PR is still Draft/unmerged and required external release evidence is absent.
```
