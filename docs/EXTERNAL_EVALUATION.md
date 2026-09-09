# External Detection Evaluation Runbook

This runbook prepares AegisLog for a truthful v1.6.1 external detection evaluation. It does not create, imply, or substitute for real external evidence.

## 1. Freeze the evaluated code

Select the exact `main` commit intended for evaluation and record its full lowercase 40-character SHA. Do not change detection behavior after the dataset has been evaluated and still claim the older results apply to the newer code.

## 2. Obtain an authorized dataset

Use telemetry that you are authorized to evaluate. Record:

- dataset owner/source and authorization basis;
- collection environment and time period;
- sampling method and inclusion/exclusion rules;
- log/source types represented;
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

## 4. Validate the dataset before generating release evidence

Run the evaluator first and inspect both aggregate and per-category results:

```bash
python tools/evaluate_detections.py /path/to/reviewed-external.jsonl \
  --dataset-kind external \
  --provenance "<truthful source, sampling, labeling, and sanitization description>" \
  --min-severity MEDIUM \
  --json
```

Do not tune labels to make the metrics look better. Investigate false positives and false negatives as engineering findings. If detection code changes, freeze the new commit and repeat the evaluation from the beginning.

## 5. Generate release evidence

Only after authorization, sanitization, and independent labeling are genuinely complete:

```bash
python tools/build_external_evidence.py /path/to/reviewed-external.jsonl \
  --evaluated-commit <40-character-evaluated-commit-sha> \
  --provenance "<truthful provenance of at least 20 characters>" \
  --labeling-procedure "<truthful labeling procedure of at least 20 characters>" \
  --reviewer "<real reviewer identity>" \
  --reviewer-role "<real reviewer role>" \
  --independent-labeling \
  --sanitized
```

This writes `evaluation/external-release-evidence.json`, records the dataset SHA-256, metrics, confidence intervals, evaluated commit, provenance, reviewer metadata, and limitations.

## 6. Preserve the evidence-only commit model

The generated evidence file must be committed as the immediate direct single-parent child of the exact evaluated code commit, with no unrelated changes. This lets release preflight verify that the evidence describes the code that was actually evaluated.

Before committing, verify:

```bash
git diff -- evaluation/external-release-evidence.json
git status --short
```

Only the evidence file should be part of the evidence-only release commit.

## 7. Release preflight and publication

Run the repository's guarded v1.6.1 release preflight/workflow from the evidence-only commit. Stop if parentage, evaluated SHA, evidence, version, tag, confirmation, CI, package, security, checksum, or provenance checks fail.

Do not claim v1.6.1 is released until the GitHub Release actually exists and its published artifacts have been verified.

## 8. Post-release verification

After publication, verify the downloaded release artifact rather than a temporary Actions artifact:

- SHA-256 matches the published checksum;
- build provenance/attestation is available;
- `AegisLog.exe --help` works on a clean Windows machine;
- `doctor` works;
- a local sample analysis works without network access;
- remote AI remains disabled by default;
- local Ollama remains optional and local;
- public documentation is updated from v1.6.0 to v1.6.1 only after these checks pass.

## Evidence integrity rules

Never fabricate authorization, provenance, sanitization, reviewer identity, independent labeling, metrics, or release verification. Synthetic fixtures and public demo logs are useful regression inputs but must not be represented as deployment-specific real-world evidence. Public research datasets may be useful for additional benchmarking when their license and labels fit AegisLog's evaluation schema, but their results must retain the dataset's actual provenance and limitations.