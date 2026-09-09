# AegisLog AI v1.6.1 Release Readiness Checklist

This checklist is the operator-facing gate for publishing permanent GitHub Release assets for `v1.6.1`.

A checked item means the requirement has been verified with evidence. Unchecked mandatory items remain release blockers or pending operator actions.

## Candidate identity

AegisLog v1.6.1 uses two distinct commit identities:

- **Evaluated code commit:** exact `main` commit evaluated against the external dataset.
- **Evidence-only release commit:** immediate single-parent child of the evaluated code commit that changes exactly `evaluation/external-release-evidence.json`.

- [x] `pyproject.toml` declares version `1.6.1`.
- [x] `src/aegislog/__init__.py` declares `__version__ = "1.6.1"`.
- [x] The repository contains `docs/RELEASE_V1.6.1.md`.
- [x] PR #77 was merged into `main`.
- [ ] The latest intended v1.6.1 evaluated code commit has been frozen and recorded.
- [ ] The exact evidence-only release commit has been created and recorded.

Evaluated code commit SHA:

```text
PENDING
```

Evidence-only release commit SHA:

```text
PENDING
```

## Candidate validation

For the exact evaluated code commit selected for v1.6.1:

- [ ] Record the exact evaluated code commit SHA.
- [ ] Confirm no unreviewed code/workflow/dependency changes occur after it is frozen.
- [ ] Confirm the required CI, security, package, Windows, runtime-lock, build-lock, and validation-lock workflows are acceptable for the selected candidate.

Historical PR runs are supporting evidence only; they do not replace validation of the final candidate actually selected for release.

## External release evidence

Current status: **BLOCKED — qualifying external evidence has not yet been established for the final v1.6.1 candidate.**

Before release:

- [ ] Obtain a real, authorized, sanitized, independently labeled external evaluation dataset.
- [ ] Keep underlying production/customer telemetry out of the repository unless explicitly authorized and safely sanitized.
- [ ] Generate `evaluation/external-release-evidence.json` using `tools/build_external_evidence.py` with `--evaluated-commit` set to the exact evaluated code commit.
- [ ] Include truthful provenance, labeling procedure, reviewer metadata, independent-labeling confirmation, and sanitization confirmation.
- [ ] Verify dataset SHA-256, sample count, metrics, uncertainty, limitations, and reviewer metadata.
- [ ] Review the generated evidence for accuracy before committing it.

Then create the release commit:

- [ ] Start from the exact evaluated code commit on `main`.
- [ ] Commit only `evaluation/external-release-evidence.json`.
- [ ] Confirm the new commit has exactly one parent and that parent is the evaluated code commit.
- [ ] Confirm no code, workflow, docs, dependencies, lockfiles, or other paths changed in the evidence-only commit.
- [ ] Record the resulting evidence-only release commit SHA.
- [ ] Confirm `tools/release_preflight.py` accepts the evidence manifest and commit binding.

Do not substitute fabricated reviewer metadata, synthetic-only evidence, placeholder provenance, or a manual checkbox for real external evidence.

## Windows release artifact

The current v1.6.1 workflow builds an **unsigned** one-file `AegisLog.exe` and publishes it with a SHA-256 checksum after validation.

Windows Authenticode signing is **optional** for this release path and is not a mandatory readiness blocker.

Required artifact checks:

- [ ] Build exactly one customer executable: `AegisLog.exe`.
- [ ] Run release smoke tests against the built executable.
- [ ] Generate `AegisLog.exe.sha256`.
- [ ] Verify the checksum before publication.
- [ ] Create build provenance attestation.
- [ ] Publish exactly the executable and checksum as GitHub Release assets.

Permanent customer assets:

```text
AegisLog.exe
AegisLog.exe.sha256
```

GitHub Actions artifacts are temporary validation evidence, not the permanent customer download channel.

## Release workflow guardrails

Workflow: `.github/workflows/release-v1.6.1.yml`

Before dispatch:

- [ ] `main` points to the exact evidence-only release commit.
- [ ] The evidence-only release commit is the direct single-parent child of the evaluated code commit.
- [ ] Its only changed path is `evaluation/external-release-evidence.json`.
- [ ] Use the exact workflow confirmation value `RELEASE-v1.6.1`.
- [ ] Confirm tag `v1.6.1` does not already exist.
- [ ] Confirm a GitHub Release named/tagged `v1.6.1` does not already exist.
- [ ] Confirm release preflight passes repository/ref, release SHA, evidence binding, tag, version, confirmation, and external-evidence checks.

The workflow must refuse publication if any mandatory gate fails.

## Post-publication verification

After the GitHub Release is published:

- [ ] Confirm the release/tag targets the evidence-only release commit.
- [ ] Confirm that commit is correctly bound to the intended evaluated code commit.
- [ ] Download `AegisLog.exe` and `AegisLog.exe.sha256` from the public `v1.6.1` GitHub Release page.
- [ ] Verify the downloaded executable against the published checksum.
- [ ] Run a clean-machine smoke test using the published release artifact rather than a CI artifact.
- [ ] Confirm `AegisLog.exe --version` reports `1.6.1`.
- [ ] Confirm the primary command surface opens successfully.
- [ ] Confirm `dashboard`, `incidents`, and `investigate` work with sanitized example data.
- [ ] Confirm remote AI remains disabled by default and local core analysis works without network access.
- [ ] Update README/docs stable-release links from v1.6.0 to v1.6.1 only after publication succeeds and is verified.
- [ ] Record the final public executable SHA-256 in the release notes or verification documentation.

Because the executable is unsigned, Windows SmartScreen or endpoint-security reputation warnings may appear. Do not misrepresent those warnings as checksum or provenance failures by themselves.

## Screenshot / README promotion

- [ ] Real Windows screenshots are captured from the exact published v1.6.1 executable if they will be labeled as stable-release screenshots.
- [ ] Screenshot source commit/release provenance is recorded.
- [ ] Screenshots contain no credentials, tokens, personal data, production logs, private hostnames, or customer information.
- [ ] README screenshot captions describe only behavior visible in the exact released build.

## Release decision

Current decision:

```text
NOT READY FOR PUBLICATION
Reason: qualifying external evaluation evidence for the final intended v1.6.1 candidate is still outstanding, and the evidence-only release commit has not yet been created and validated.
```

Mandatory Windows code signing is not part of the current blocker list.