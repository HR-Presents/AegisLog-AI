# AegisLog AI v1.6.1 — Release Handoff

Use this handoff together with the v1.6.1 release checklist, go/no-go record, blocker-owner list, and external-evidence guide. It is an operational handoff, not authorization to bypass a release gate.

## Current state

- PR #77 has already been merged.
- Additional validated UI and public-documentation work has landed on `main` since that original candidate.
- The exact final v1.6.1 evaluated code commit has not yet been frozen.
- Qualifying real external evaluation evidence has not yet been established for the final candidate.
- The current v1.6.1 workflow publishes an **unsigned** standalone Windows executable plus SHA-256 checksum.
- Windows Authenticode signing is optional and is not a mandatory v1.6.1 blocker.

## Handoff to candidate owner

Choose the exact `main` commit intended for v1.6.1 and freeze it before external evidence generation.

Record that commit as the **evaluated code commit**. Do not generate final evidence against a moving branch or an older candidate after later product changes have landed.

Confirm the required CI, security, package, Windows-build, runtime-lock, build-lock, and validation-lock checks are acceptable for that candidate.

## Handoff to external dataset owner and independent reviewer

Provide a real, authorized, sanitized external evaluation dataset. Do not use repository synthetic/demo fixtures as external evidence and do not derive expected labels from AegisLog output.

Document provenance, source/sampling, relevant environment/source types, sanitization, authorization/data handling, material limitations, reviewer identity/role, labeling procedure, category definitions, and adjudication where applicable.

Do not commit sensitive raw telemetry, credentials, secrets, customer identifiers, or unnecessary personal information.

If independent labeling or sanitization cannot truthfully be confirmed, stop.

## Handoff to evidence operator

After the exact evaluated code commit is frozen:

1. Run the real external evaluation against that exact commit.
2. Generate `evaluation/external-release-evidence.json` with `tools/build_external_evidence.py` and set `evaluated_commit` to that exact code SHA.
3. Include truthful independent-labeling and sanitization assertions plus genuine reviewer/provenance metadata.
4. Verify dataset SHA-256, sample count, metrics, uncertainty, limitations, and reviewer metadata.
5. Commit **only** `evaluation/external-release-evidence.json` as the immediate direct child of the evaluated code commit.
6. Record the resulting evidence-only child SHA. This becomes the release commit for the guarded workflow.

`tools/release_preflight.py` must reject stale evidence, arbitrary ancestor evidence, merge commits, and evidence commits containing unrelated changed paths.

## Handoff to release operator

Immediately before dispatch:

1. Confirm `main` points exactly to the intended evidence-only release commit.
2. Confirm it has exactly one parent and that parent equals evidence field `evaluated_commit`.
3. Confirm the parent-to-release diff contains only `evaluation/external-release-evidence.json`.
4. Confirm version metadata remains `1.6.1`.
5. Confirm genuine external evidence and release notes/checklists are complete.
6. Confirm no existing `v1.6.1` tag or GitHub Release exists.
7. Confirm no later unreviewed commit has moved `main` beyond the evidence-only release commit.

Then dispatch `.github/workflows/release-v1.6.1.yml` from `main` with:

```text
RELEASE-v1.6.1
```

Do not weaken or bypass a failing preflight, validation, checksum, provenance, smoke-test, or immutability gate.

The production release must come from the guarded release workflow. PR Actions artifacts are temporary validation evidence and must not be relabeled as permanent customer downloads.

## Handoff to post-release verifier

After successful publication:

- confirm the release targets the intended evidence-only release commit;
- confirm the public release contains exactly `AegisLog.exe` and `AegisLog.exe.sha256`;
- verify the downloaded executable against the published checksum;
- perform clean-machine smoke testing using the public GitHub Release executable;
- confirm remote AI remains disabled by default and local core analysis works without network access;
- update stable-release README/docs references only after publication is verified.

Because the release executable is unsigned, Windows SmartScreen or endpoint-security reputation warnings may appear. Treat those as distribution/reputation behavior, not as proof of checksum failure.

Stable screenshots must come from the exact published executable if they are labeled as release screenshots.

## Stop conditions

Keep the release NO-GO if the evaluated code SHA is ambiguous; external evidence is synthetic, circularly labeled, unsanitized, unauthorized, fabricated, or stale; the release commit is not a direct evidence-only child; a tag/release collision exists; any required workflow gate fails; checksum/provenance/smoke verification fails; or a material security/correctness issue is discovered.