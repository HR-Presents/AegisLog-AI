# External detection evidence for release

AegisLog's checked-in `evaluation/labeled_events.jsonl` is a small synthetic regression fixture. It protects known behavior but is not sufficient evidence for production detection-effectiveness claims.

The v1.6.0 release preflight therefore requires a reviewed, sanitized metadata manifest at:

`evaluation/external-release-evidence.json`

Do **not** commit raw production logs merely to satisfy this gate. The manifest records the provenance and results of an independently labeled external evaluation while the underlying authorized telemetry may remain in the organization's approved storage system.

## Required JSON shape

```json
{
  "schema_version": 1,
  "dataset_kind": "external",
  "provenance": "Meaningful description of the authorized telemetry population and sampling method.",
  "labeling_procedure": "Meaningful description of how ground-truth labels were assigned and reviewed.",
  "reviewer": "Reviewer name or approved organizational reviewer identifier",
  "reviewer_role": "Security / detection-review role",
  "independent_labeling": true,
  "sanitized": true,
  "dataset_sha256": "<64 lowercase hexadecimal characters>",
  "evaluated_commit": "<40 lowercase hexadecimal Git commit SHA>",
  "sample_count": 1,
  "metrics": {
    "precision": 0.0,
    "recall": 0.0,
    "case_accuracy": 0.0,
    "false_positives": 0,
    "false_negatives": 0
  }
}
```

The numeric values above illustrate the schema only. Do not copy placeholder results into a release manifest.

## Release binding

`tools/release_preflight.py` requires the manifest's `evaluated_commit` to exactly equal `GITHUB_SHA` for the release dispatch. Results from an older commit cannot authorize a later release.

The preflight also requires:

- repository `HR-Presents/AegisLog-AI`;
- dispatch from `refs/heads/main`;
- an exact release tag/version/confirmation match;
- a 40-hex-character Windows signing certificate thumbprint;
- a credential-free HTTPS RFC3161 timestamp URL;
- `dataset_kind` equal to `external`;
- `independent_labeling` and `sanitized` both explicitly `true`;
- a positive sample count;
- precision, recall, and exact-case accuracy between 0 and 1;
- non-negative false-positive and false-negative counts;
- non-placeholder provenance and labeling descriptions.

The preflight validates evidence integrity and binding, not scientific representativeness by itself. Reviewers must still judge whether the dataset population, sampling method, class distribution, labeling quality, reviewer independence, and known exclusions are appropriate for the intended deployment.

## Recommended review record

Before adding the manifest, retain the underlying evaluation report and dataset in approved organizational storage, record who performed the labeling and review, document sanitization, record the dataset SHA-256, and run the evaluator against the exact release candidate commit. Add only the sanitized manifest through a reviewed pull request.

If the release candidate changes after evaluation, regenerate/review the evidence for the new commit rather than editing only the SHA field.
