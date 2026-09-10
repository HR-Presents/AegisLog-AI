# External Detection Evaluation Runbook

This runbook prepares AegisLog for truthful external detection evaluation. It does not create, imply, or substitute for real external evidence.

## 1. Freeze the evaluated code

Select the exact `main` commit intended for evaluation and record its full lowercase 40-character SHA. Do not change detection behavior after the dataset has been evaluated and still claim the older results apply to the newer code.

## 2. Obtain an authorized dataset

Use telemetry that you are authorized to evaluate. Record all of the following before running AegisLog:

- dataset owner/source and authorization basis;
- collection environment and collection period;
- sampling method and inclusion/exclusion rules;
- every log/source type represented;
- known class balance or enrichment;
- sanitization performed before AegisLog receives the data;
- important differences from expected deployment environments.

Do not commit raw sensitive telemetry to this repository.

## 3. Create independent labels

Labels must be produced or independently reviewed without using AegisLog's output as the ground truth. Record the reviewer identity and role truthfully, the labeling procedure, category definitions, disagreement handling, and any uncertain cases.

The evaluator expects JSONL cases shaped like:

```json
{"id":"case-001","label":"benign-auth","lines":["<sanitized log line>"],"expected_categories":[]}
{"id":"case-002","label":"reviewed-security-event","lines":["<sanitized log line 1>","<sanitized log line 2>"],"expected_categories":["<AegisLog category>"]}
```

Each `id` must be unique. `lines` must be a non-empty list of strings. `expected_categories` must contain unique AegisLog detection-category strings. A benign case normally has an empty category list.

## 4. Validate the dataset

Run the evaluator first and inspect aggregate, confidence-interval, case-level, and per-category results:

```bash
python tools/evaluate_detections.py /path/to/reviewed-external.jsonl \
  --dataset-kind external \
  --provenance "<truthful source, sampling, labeling, and sanitization description>" \
  --min-severity MEDIUM \
  --json
```

Do not tune labels to make the metrics look better. Investigate false positives and false negatives as engineering findings. If detection code changes, freeze the new commit and repeat the evaluation from the beginning.

## 5. Generate schema-v2 evidence

Only after authorization, sanitization, and independent labeling are genuinely complete:

```bash
python tools/build_external_evidence.py /path/to/reviewed-external.jsonl \
  --evaluated-commit <40-character-evaluated-commit-sha> \
  --provenance "<truthful provenance of at least 20 characters>" \
  --labeling-procedure "<truthful labeling procedure of at least 20 characters>" \
  --reviewer "<real reviewer identity>" \
  --reviewer-role "<real reviewer role>" \
  --source-type "linux-auth" \
  --source-type "application" \
  --collection-period "<truthful collection period>" \
  --sampling-method "<truthful sampling method of at least 20 characters>" \
  --known-exclusions "<known exclusions, or 'none known' when that is true>" \
  --independent-labeling \
  --sanitized
```

`--source-type` is repeatable. Use the actual source types represented by the dataset rather than desired deployment coverage.

The generator writes `evaluation/external-release-evidence.json`. Schema v2 records the dataset SHA-256, evaluated commit, dataset profile, derived benign/positive class balance, expected-category counts, aggregate metrics, per-category metrics, confidence intervals, reviewer metadata, and limitations.

## 6. Preserve the evidence-only commit model

The generated evidence file must be committed as the immediate direct single-parent child of the exact evaluated code commit, with no unrelated changes. This allows release preflight to verify that the evidence describes the code that was actually evaluated.

Before committing, verify:

```bash
git diff -- evaluation/external-release-evidence.json
git status --short
```

Only the evidence file should be part of the evidence-only release commit.

## 7. Release preflight

When a release elects to bind external evidence, `tools/release_preflight.py` requires schema v2 and validates the evidence structure before verifying the direct-child binding. A release without external evidence remains permitted unless its release policy explicitly makes external evidence mandatory.

External evidence is not a substitute for the repository's normal CI, security, package, Windows-build, and dependency-lock gates.

## 8. Post-evaluation review

Before citing results publicly, review:

- whether the dataset population resembles the intended deployment;
- whether sampling enriched positives or otherwise changed prevalence;
- whether important source types are absent;
- whether labels were created independently and disagreements were handled consistently;
- whether false positives and false negatives cluster by category;
- confidence-interval width and sample size;
- dataset shift or collection limitations.

Do not convert a strong result on one external dataset into a general claim of production effectiveness.

## Evidence integrity rules

Never fabricate authorization, provenance, collection period, source types, sampling method, exclusions, sanitization, reviewer identity, independent labeling, metrics, or release verification. Synthetic fixtures and public demo logs are useful regression inputs but must not be represented as deployment-specific real-world evidence. Public research datasets may be useful for additional benchmarking when their license and labels fit AegisLog's evaluation schema, but their results must retain the dataset's actual provenance and limitations.
