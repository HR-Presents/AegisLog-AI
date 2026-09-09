# AegisLog AI v1.6.1 release go/no-go

Status: **NO-GO for public publication**

This document records current release-readiness state. It does not authorize tagging or publication.

## Current project state

- Published stable release: `v1.6.0`.
- v1.6.1 is not published.
- PR #77 has already been merged.
- Additional validated UI and public-documentation improvements have landed on `main` since the original candidate evidence point.
- The exact final v1.6.1 evaluated code commit has therefore not yet been frozen.
- Qualifying real external evaluation evidence has not yet been established for that final candidate.

## GO items

- [x] v1.6.1 version metadata is aligned.
- [x] Dedicated guarded v1.6.1 release workflow exists.
- [x] Release workflow requires dispatch from `main` with exact confirmation `RELEASE-v1.6.1`.
- [x] Release workflow runs quality, security, packaging, checksum, provenance, and smoke-test gates.
- [x] Release workflow builds a one-file Windows `AegisLog.exe` and publishes only the executable plus checksum.
- [x] External-evidence generation and reviewer submission procedures are documented.
- [x] Release preflight supports the direct single-parent evidence-only child model and rejects unrelated changes.
- [x] Mandatory Windows Authenticode signing has been removed from the current v1.6.1 release path.

## NO-GO blockers

### 1. Final evaluated code commit is not frozen

The repository has moved beyond the older PR #77 candidate through later validated product/UI and documentation work. The exact code commit intended for v1.6.1 must be selected and frozen before external evaluation evidence is generated.

### 2. External release evidence is not yet available

`evaluation/external-release-evidence.json` must be generated from a real, authorized, sanitized, independently labeled external dataset evaluated against the exact frozen code commit.

The evidence must truthfully record provenance, labeling procedure, reviewer identity/role, metrics, uncertainty, limitations, and the exact evaluated commit. Repository synthetic/demo fixtures must not be substituted for external evidence.

### 3. Final release commit must be an evidence-only child

After external evidence is generated for the frozen evaluated code commit, create one immediate child commit that changes only:

```text
evaluation/external-release-evidence.json
```

`tools/release_preflight.py` must verify that:

- the release commit has exactly one parent;
- that parent equals the evidence field `evaluated_commit`;
- the parent-to-release diff contains exactly `evaluation/external-release-evidence.json`.

### 4. Release workflow has not run

No v1.6.1 GitHub Release currently exists. The guarded workflow must run from the exact evidence-only release commit on `main` and all mandatory validation, checksum, provenance, and smoke-test gates must pass.

### 5. Post-publication verification remains required

After legitimate publication, independently verify the release target, exact asset set, SHA-256 checksum, and clean-machine smoke behavior using the public GitHub Release artifact.

The current release path publishes an **unsigned** executable. Windows signing is optional and is not a NO-GO blocker.

## Release decision

```text
NO-GO
```

Reasons:

1. The final intended v1.6.1 evaluated code commit has not been frozen.
2. Required genuine external release evidence is absent for that final candidate.
3. The evidence-only release child does not yet exist.
4. The guarded v1.6.1 release workflow has not run on the final release commit.

A GO decision is appropriate only after these blockers are resolved with truthful evidence tied to the exact code commit selected for release.