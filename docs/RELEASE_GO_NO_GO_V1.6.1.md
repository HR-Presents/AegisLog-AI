# AegisLog AI v1.6.1 release go/no-go

Status: **NO-GO for production publication**

This document records the release-readiness state observed on the PR branch. It is not authorization to merge, tag, or publish.

## Candidate validation

Current PR branch head reviewed for this status:

```text
1856a53c7d632cadce0049f0fb191e5e9e833bab
```

All seven pull-request workflows completed successfully for that exact head:

- Validation toolchain lock audit #181
- Security checks #1320
- Build toolchain lock audit #197
- Runtime lock audit #205
- CI #1338
- Package build #458
- Windows single executable #418

Matching temporary Windows CI artifact:

```text
Name: AegisLog-Windows-Single-EXE
Artifact ID: 10072121093
Artifact digest: sha256:5702bd24642278fb3046ac4afa173860a38b97c9c513c32eac8b92d661d2b1d2
Head SHA: 1856a53c7d632cadce0049f0fb191e5e9e833bab
```

This artifact is temporary pull-request validation evidence. It is not the signed v1.6.1 customer release asset.

## GO items

- [x] v1.6.1 version metadata is aligned in `pyproject.toml` and `src/aegislog/__init__.py`.
- [x] Dedicated guarded v1.6.1 release workflow exists.
- [x] Release workflow requires dispatch from `main` with exact confirmation `RELEASE-v1.6.1`.
- [x] Release workflow runs quality, security, packaging, checksum, signing, provenance, and smoke-test gates.
- [x] Release workflow publishes only `AegisLog.exe` and `AegisLog.exe.sha256` as GitHub Release assets after successful gates.
- [x] Exact current PR head has seven successful PR validation workflows.
- [x] Exact current PR head produced a matching Windows validation artifact.
- [x] No existing GitHub Release named `v1.6.1` was found during this review.
- [x] No existing Git tag `v1.6.1` was found during this review.
- [x] External-evidence generation and reviewer submission procedures are documented.
- [x] Windows signing requirements and fail-closed verification are documented.

## NO-GO blockers

### 1. Pull request lifecycle

PR #77 is still Draft, open, mergeable, and unmerged. The release workflow requires execution from `main`, so this branch is not a valid production release source yet.

Do not merge or mark ready solely because this checklist exists. Normal review and project authorization still apply.

### 2. External release evidence

`evaluation/external-release-evidence.json` is absent on the current PR branch.

The release preflight requires this file. It must be generated from a real sanitized external JSONL dataset with independently assigned labels, real provenance, a documented labeling procedure, real reviewer identity/role, and the exact release candidate commit.

Synthetic repository fixtures must not be relabeled as external evidence.

### 3. Windows signing configuration

The repository workflow requires these externally provisioned settings:

```text
Secret: WINDOWS_SIGNING_PFX_BASE64
Secret: WINDOWS_SIGNING_PFX_PASSWORD
Secret: WINDOWS_SIGNING_CERT_THUMBPRINT
Variable: WINDOWS_SIGNING_TIMESTAMP_URL
```

The connected repository interface cannot inspect secret values or reliably prove their presence. An authorized repository administrator must confirm configuration without exposing the values.

The timestamp URL must be HTTPS. The certificate must contain the Code Signing EKU, expose the private key after import, match the configured thumbprint, successfully sign the executable, and produce a verifiable RFC3161 timestamp.

### 4. Final release candidate must be the merged `main` commit

The exact PR head above is validated, but it is not yet the final release candidate because it has not been merged to `main`.

After approved merge, record the resulting exact `main` commit SHA and bind external evidence to that exact candidate. If the merge commit differs from the PR head, do not reuse evidence whose `evaluated_commit` points to the PR head.

### 5. Release workflow has not run

No production v1.6.1 release workflow has been authorized or executed by this status review.

The release remains NO-GO until the exact merged candidate passes the guarded release workflow, including signing, checksum verification, attestation, smoke testing, and final publication checks.

### 6. Post-publication verification is still required

After a legitimate release is published, independently verify the assets downloaded from the GitHub Release page:

- SHA-256 matches `AegisLog.exe.sha256`;
- Authenticode status is valid;
- signer thumbprint matches the approved release identity;
- RFC3161 timestamp is present;
- clean-machine smoke tests succeed;
- published release points to the intended commit;
- only the intended release assets are present.

## Release decision

Current decision:

```text
NO-GO
```

Reasons:

1. PR #77 is Draft and unmerged.
2. Required external release evidence is absent.
3. Signing-secret/variable provisioning cannot yet be confirmed from repository-visible state.
4. The final merged `main` candidate does not yet exist for this change set.
5. The guarded v1.6.1 release workflow has not run against that final candidate.

A GO decision is appropriate only after every blocker above is resolved with evidence tied to the exact release commit.
