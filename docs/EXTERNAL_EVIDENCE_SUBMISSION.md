# External release evidence submission template

Use this template when preparing the real external detection evidence required for an AegisLog release. This is an audit record, not a checkbox exercise. Do not fabricate reviewer identity, provenance, labels, or sanitization claims.

## Release candidate identities

AegisLog v1.6.1 intentionally uses two distinct commits for release evidence:

1. **Evaluated code commit** — the exact reviewed `main` commit whose code is evaluated against the external dataset.
2. **Evidence-only release commit** — the immediate single-parent child of the evaluated code commit that changes exactly `evaluation/external-release-evidence.json` and no other path.

Record:

- **Release version:** `v1.6.1`
- **Evaluated code commit SHA:** `<40-character lowercase Git SHA>`
- **Evidence-only release commit SHA:** `<filled only after the evidence file is committed>`
- **Dataset file:** `<path to external JSONL dataset>`
- **Minimum reported severity:** `MEDIUM` unless an approved release decision changes it

`evaluated_commit` in the evidence JSON must equal the evaluated code commit, not the evidence-only release commit. Evidence generated for another code commit must not be relabeled or reused.

The release workflow must be dispatched from the evidence-only release commit. `tools/release_preflight.py` verifies that this release commit has exactly one parent, that its parent equals `evaluated_commit`, and that the only changed path is `evaluation/external-release-evidence.json`.

## Dataset provenance

Provide a concrete description of where the dataset came from and how it was selected. The generator requires at least 20 characters, but the release record should be much more specific.

**Provenance:**

> `<Describe the source environment or public/external dataset, collection period if relevant, sampling method, inclusion/exclusion criteria, and why the sample is representative enough for this release evaluation. Do not include secrets or customer-identifying details.>`

## Labeling procedure

The labels must be assigned independently of AegisLog's output. Do not run the detector first and then copy its categories into the expected labels.

**Labeling procedure:**

> `<Describe who labeled the cases, what reference criteria were used, whether the reviewer saw detector output, how disagreements were handled, and how expected_categories were selected.>`

## Reviewer

- **Reviewer:** `<real reviewer name or stable organizational identity>`
- **Reviewer role:** `<role, e.g. security analyst, detection engineer, independent reviewer>`
- **Independent labeling confirmed:** `yes / no`

`independent_labeling` may only be set when the labels were established independently of the AegisLog results being evaluated.

## Sanitization

- **Dataset sanitized for release evidence:** `yes / no`
- **Sanitization performed by:** `<person or team>`
- **Sanitization method:** `<brief method>`

Before setting `sanitized`, confirm that the dataset contains no credentials, tokens, secrets, customer names, personal data, private production hostnames/domains, sensitive internal paths, or other information that should not be retained in release evidence.

Prefer irreversible replacement with synthetic identifiers or documentation-reserved values. Do not rely on visual blurring because the dataset is machine-readable text.

## JSONL case schema

The external dataset is newline-delimited JSON. Every non-empty line must be one JSON object with:

- `id`: unique non-empty string
- `lines`: non-empty array of log-line strings
- `expected_categories`: array of unique category strings independently assigned by the reviewer
- `label`: optional descriptive string

Example structure only — do not submit synthetic examples as external release evidence:

```json
{"id":"ext-001","label":"SSH authentication failures","lines":["<sanitized external log line>","<sanitized external log line>"],"expected_categories":["authentication"]}
```

A negative/control case can use an empty `expected_categories` array when the independent reviewer expects no qualifying detection at the configured minimum severity.

## Pre-generation checks

Confirm all of the following before generating evidence:

- [ ] PR #77 has completed required human review and has been merged to `main`.
- [ ] The exact evaluated code commit on `main` is frozen and recorded.
- [ ] Dataset is external to the repository's synthetic regression fixtures.
- [ ] Every case has a unique `id`.
- [ ] Every case has at least one string in `lines`.
- [ ] `expected_categories` contains only independently assigned expected labels and has no duplicates.
- [ ] Reviewer identity and role are real and recorded.
- [ ] Provenance is accurate and sufficiently detailed.
- [ ] Labeling procedure is accurate and sufficiently detailed.
- [ ] Independent labeling is genuinely satisfied.
- [ ] Sanitization has been completed and reviewed.

## Evidence generation command

Run from the repository root after the evaluated code commit is fixed:

```bash
python tools/build_external_evidence.py <external-dataset.jsonl> \
  --evaluated-commit <40-character-lowercase-evaluated-code-SHA> \
  --provenance "<real provenance description>" \
  --labeling-procedure "<real independent labeling procedure>" \
  --reviewer "<real reviewer identity>" \
  --reviewer-role "<real reviewer role>" \
  --independent-labeling \
  --sanitized \
  --min-severity MEDIUM \
  --output evaluation/external-release-evidence.json
```

The generator refuses to overwrite an existing evidence file. Resolve stale evidence deliberately; do not weaken that protection.

## Generated evidence review

After generation, review `evaluation/external-release-evidence.json` and verify:

- `schema_version` is supported.
- `dataset_kind` is `external`.
- `dataset_sha256` matches the exact dataset used for evaluation.
- `evaluated_commit` equals the exact evaluated code commit SHA.
- `provenance`, `labeling_procedure`, `reviewer`, and `reviewer_role` are accurate.
- `independent_labeling` and `sanitized` are both true only because those requirements were actually satisfied.
- `sample_count` is plausible for the submitted dataset.
- Precision, recall, case accuracy, false positives, false negatives, and confidence intervals were generated from the submitted dataset rather than copied manually.
- Limitations remain visible in the final evidence record.

## Evidence-only release commit

Only after the evidence JSON has been reviewed:

1. Confirm the working branch is `main` at the exact evaluated code commit.
2. Add only `evaluation/external-release-evidence.json`.
3. Create one normal commit with the evaluated code commit as its only parent.
4. Confirm no code, workflow, documentation, dependency, lockfile, or other file changed in that commit.
5. Record the resulting evidence-only release commit SHA.
6. Dispatch the guarded v1.6.1 release workflow from that evidence-only release commit only after all other release gates are satisfied.

Do not amend the evaluated code commit to include the evidence file. Do not combine the evidence file with any other change. Do not use a merge commit for the evidence-only release commit.

## Approval record

- **Dataset owner / provider:** `<name or organization>`
- **Evidence reviewer:** `<name or organization>`
- **Release operator:** `<name or organization>`
- **Review date:** `<YYYY-MM-DD>`
- **Decision:** `approved / rejected`
- **Notes:** `<important limitations, sampling caveats, or reasons for rejection>`

AegisLog v1.6.1 must not be published if the required external evidence is absent, fabricated, tied to the wrong evaluated code commit, unsanitized, not independently labeled, or committed in a release commit that violates the evidence-only direct-child rule.
