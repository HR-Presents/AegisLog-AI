# External release evidence submission template

Use this template when preparing the real external detection evidence required for an AegisLog release. This is an audit record, not a checkbox exercise. Do not fabricate reviewer identity, provenance, labels, or sanitization claims.

## Release candidate

- **Release version:** `v1.6.1`
- **Evaluated commit SHA:** `<40-character lowercase Git SHA>`
- **Dataset file:** `<path to external JSONL dataset>`
- **Minimum reported severity:** `MEDIUM` unless an approved release decision changes it

The evaluated commit must be the exact reviewed candidate intended for release. Evidence generated for a different commit must not be relabeled for the release candidate.

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

- [ ] Dataset is external to the repository's synthetic regression fixtures.
- [ ] Every case has a unique `id`.
- [ ] Every case has at least one string in `lines`.
- [ ] `expected_categories` contains only independently assigned expected labels and has no duplicates.
- [ ] Reviewer identity and role are real and recorded.
- [ ] Provenance is accurate and sufficiently detailed.
- [ ] Labeling procedure is accurate and sufficiently detailed.
- [ ] Independent labeling is genuinely satisfied.
- [ ] Sanitization has been completed and reviewed.
- [ ] Evaluated commit is the exact release candidate.

## Evidence generation command

Run from the repository root after the candidate commit is known:

```bash
python tools/build_external_evidence.py <external-dataset.jsonl> \
  --evaluated-commit <40-character-lowercase-Git-SHA> \
  --provenance "<real provenance description>" \
  --labeling-procedure "<real independent labeling procedure>" \
  --reviewer "<real reviewer identity>" \
  --reviewer-role "<real reviewer role>" \
  --independent-labeling \
  --sanitized \
  --min-severity MEDIUM \
  --output evaluation/external-release-evidence.json
```

The generator refuses to overwrite an existing evidence file. Remove or archive stale evidence only through the normal reviewed repository process; do not silently replace it during release preparation.

## Generated evidence review

After generation, review `evaluation/external-release-evidence.json` and verify:

- `schema_version` is supported.
- `dataset_kind` is `external`.
- `dataset_sha256` matches the exact dataset used for evaluation.
- `evaluated_commit` is the exact release candidate SHA.
- `provenance`, `labeling_procedure`, `reviewer`, and `reviewer_role` are accurate.
- `independent_labeling` and `sanitized` are both true only because those requirements were actually satisfied.
- `sample_count` is plausible for the submitted dataset.
- Precision, recall, case accuracy, false positives, false negatives, and confidence intervals were generated from the submitted dataset rather than copied manually.
- Limitations remain visible in the final evidence record.

## Approval record

- **Dataset owner / provider:** `<name or organization>`
- **Evidence reviewer:** `<name or organization>`
- **Release operator:** `<name or organization>`
- **Review date:** `<YYYY-MM-DD>`
- **Decision:** `approved / rejected`
- **Notes:** `<important limitations, sampling caveats, or reasons for rejection>`

AegisLog v1.6.1 must not be published if the required external evidence is absent, fabricated, tied to the wrong commit, unsanitized, or not independently labeled.
