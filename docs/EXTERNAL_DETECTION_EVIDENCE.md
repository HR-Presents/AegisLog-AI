# External detection evidence for release

AegisLog's checked-in `evaluation/labeled_events.jsonl` is a small synthetic regression fixture. It protects known behavior but is not sufficient evidence for production detection-effectiveness claims.

For independently reviewed external evaluation, the repository uses a sanitized metadata manifest at:

`evaluation/external-release-evidence.json`

Do **not** commit raw production logs merely to create this manifest. The evidence record can bind metrics and audit metadata to an authorized external dataset while the underlying telemetry remains in approved storage.

## Schema v2

New external evidence must use `schema_version: 2`. Schema v2 keeps the original integrity fields and adds explicit dataset-profile, class-balance, per-category, and uncertainty records so reviewers can judge what the numbers actually represent.

Required top-level fields include:

```json
{
  "schema_version": 2,
  "dataset_kind": "external",
  "provenance": "Meaningful description of the authorized telemetry population and origin.",
  "labeling_procedure": "Meaningful description of how ground-truth labels were assigned and reviewed.",
  "reviewer": "Reviewer name or approved organizational reviewer identifier",
  "reviewer_role": "Security / detection-review role",
  "independent_labeling": true,
  "sanitized": true,
  "dataset_sha256": "<64 lowercase hexadecimal characters>",
  "evaluated_commit": "<40 lowercase hexadecimal Git commit SHA>",
  "sample_count": 100,
  "minimum_reported_severity": "MEDIUM",
  "dataset_profile": {
    "source_types": ["linux-auth", "application"],
    "collection_period": "<truthful period>",
    "sampling_method": "<truthful sampling method>",
    "known_exclusions": "<truthful exclusions or none known>"
  },
  "class_balance": {
    "benign_cases": 70,
    "positive_cases": 30,
    "expected_category_case_counts": {
      "authentication": 20,
      "web": 10
    }
  },
  "metrics": {
    "precision": 0.0,
    "recall": 0.0,
    "case_accuracy": 0.0,
    "false_positives": 0,
    "false_negatives": 0
  },
  "per_category_metrics": {},
  "uncertainty": {},
  "limitations": "<generated limitations statement>"
}
```

Numeric values above illustrate the shape only. Do not copy placeholder results into an evidence manifest.

## What is derived versus declared

The generator derives these values from the exact submitted JSONL dataset and evaluator output:

- `dataset_sha256`;
- `sample_count`;
- benign and positive case counts;
- expected-category case counts;
- aggregate precision, recall, exact-case accuracy, false positives, and false negatives;
- per-category metrics;
- confidence intervals;
- evaluator limitations.

The operator must truthfully declare provenance, labeling procedure, reviewer identity/role, source types, collection period, sampling method, known exclusions, independent labeling, and sanitization. These fields cannot be inferred safely by the tool.

## Release binding

When `tools/release_preflight.py` is invoked with `--external-evidence`, it requires schema v2 and validates the evidence structure. It then verifies that the release commit is the direct single-parent child of `evaluated_commit` and that the only changed path is `evaluation/external-release-evidence.json`.

Results from an older code commit cannot authorize a later code state merely by editing the SHA field.

The preflight validates evidence integrity and binding, not scientific representativeness by itself. Reviewers must still judge the dataset population, sampling method, class distribution, labeling quality, reviewer independence, source coverage, known exclusions, and deployment similarity.

## Recommended review record

Before adding the manifest, retain the underlying evaluation report and authorized dataset in approved organizational storage. Record who performed labeling and review, document sanitization, preserve the dataset SHA-256, and run the evaluator against the exact code commit being assessed.

If detection code changes after evaluation, regenerate and review the evidence from the new code state rather than editing only `evaluated_commit`.

See [`EXTERNAL_EVALUATION.md`](EXTERNAL_EVALUATION.md) and [`EXTERNAL_EVIDENCE_SUBMISSION.md`](EXTERNAL_EVIDENCE_SUBMISSION.md) for the operational workflow.
