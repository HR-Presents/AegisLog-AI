# AegisLog AI v1.6.1 release go/no-go

Status: **NO-GO for production publication**

This document records release-readiness state on the PR branch. It is not authorization to merge, tag, or publish.

## Candidate validation

Current validated PR head:

```text
dcde3f5d147715a952e743fe3216eca6efd8344c
```

All seven pull-request workflows completed successfully for that exact head:

- Security checks #1334
- Runtime lock audit #212
- Build toolchain lock audit #204
- Validation toolchain lock audit #188
- CI #1352
- Package build #465
- Windows single executable #425

Matching temporary Windows CI artifact:

```text
Name: AegisLog-Windows-Single-EXE
Artifact ID: 10073054699
Artifact digest: sha256:b87c7ff06eecdb37e6c8765f57cad58c107d04caca88efeffcbd820513866db7
Head SHA: dcde3f5d147715a952e743fe3216eca6efd8344c
```

This artifact is temporary pull-request validation evidence. It is not the signed v1.6.1 customer release asset.

## GO items

- [x] v1.6.1 version metadata is aligned.
- [x] Dedicated guarded v1.6.1 release workflow exists.
- [x] Release workflow requires dispatch from `main` with exact confirmation `RELEASE-v1.6.1`.
- [x] Release workflow runs quality, security, packaging, checksum, signing, provenance, and smoke-test gates.
- [x] Release workflow publishes only `AegisLog.exe` and `AegisLog.exe.sha256` after successful gates.
- [x] Exact current PR head has seven successful PR validation workflows.
- [x] Exact current PR head produced a matching Windows validation artifact.
- [x] External-evidence generation and reviewer submission procedures are documented.
- [x] Release preflight no longer requires an impossible self-referential evidence SHA.
- [x] Release preflight now accepts only a direct single-parent evidence-only child of the evaluated code commit and rejects unrelated changes.
- [x] Windows signing requirements and fail-closed verification are documented.

## NO-GO blockers

### 1. Pull request lifecycle

PR #77 remains Draft/open/unmerged. The production workflow must run from `main`. Normal human review and project authorization still apply.

### 2. External release evidence is not yet available

`evaluation/external-release-evidence.json` is intentionally absent on the PR branch. It must not be fabricated from repository synthetic fixtures.

After approved merge, the exact merged `main` code SHA becomes the **evaluated commit**. A real sanitized external dataset with independently assigned labels, genuine provenance, labeling procedure, reviewer identity/role, metrics, uncertainty, and limitations must be evaluated against that SHA.

The generated evidence file must record that exact code SHA in `evaluated_commit`.

### 3. Final release commit must be an evidence-only child

Because a commit cannot contain its own Git SHA, the final release commit is intentionally distinct from the evaluated code commit.

After external evidence is generated for the frozen evaluated code SHA, create one immediate child commit that changes **only**:

```text
evaluation/external-release-evidence.json
```

That evidence-only child is the release commit. `tools/release_preflight.py` fails closed unless:

- the release commit has exactly one parent;
- that parent equals evidence field `evaluated_commit`;
- the parent-to-release diff contains exactly `evaluation/external-release-evidence.json`.

Stale evidence, arbitrary ancestor evidence, merge commits, and evidence commits containing any code/workflow/docs/dependency change are rejected.

### 4. Windows signing configuration

The workflow requires:

```text
Secret: WINDOWS_SIGNING_PFX_BASE64
Secret: WINDOWS_SIGNING_PFX_PASSWORD
Secret: WINDOWS_SIGNING_CERT_THUMBPRINT
Variable: WINDOWS_SIGNING_TIMESTAMP_URL
```

The connected repository interface cannot inspect secret values or reliably prove their presence. An authorized repository administrator must confirm configuration without exposing values. The certificate must contain Code Signing EKU/private key, match the approved thumbprint, and produce a verifiable RFC3161 timestamp through credential-free HTTPS.

### 5. Release workflow has not run

No production v1.6.1 release workflow has been authorized or executed. The guarded workflow must run from the exact evidence-only release commit on `main` and all gates must pass.

### 6. Post-publication verification remains required

After legitimate publication, independently verify release target, exact asset set, SHA-256 checksum, Authenticode signer identity/thumbprint, RFC3161 timestamp, and clean-machine smoke behavior.

## Release decision

```text
NO-GO
```

Reasons:

1. PR #77 is Draft and unmerged.
2. Required genuine external release evidence is absent.
3. The merged evaluated code commit and its evidence-only release child do not yet exist.
4. Signing configuration cannot yet be independently confirmed from repository-visible state.
5. The guarded v1.6.1 release workflow has not run on the final release commit.

A GO decision is appropriate only after every blocker is resolved with evidence tied to the exact evaluated code commit and a release commit that satisfies the strict evidence-only child relationship.
