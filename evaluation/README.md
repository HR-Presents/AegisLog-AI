# Detection evaluation

AegisLog keeps two checked-in synthetic datasets for deterministic regression testing:

- `labeled_events.jsonl` is the small core fixture used for fast, focused regression checks.
- `representative_synthetic_v21.jsonl` is a broader synthetic corpus covering benign controls and the current authentication, audit, error, network, privilege, service, and web categories across multiple log shapes.

Both datasets are synthetic. Neither is evidence of deployment-specific security effectiveness, real-world false-positive rates, or adversarial robustness.

## Dataset format

Each non-empty JSONL row must be an object with:

- `id`: unique, non-empty string;
- `lines`: non-empty list of log-event strings;
- `expected_categories`: list of expected detection categories (may be empty);
- `label`: optional descriptive string.

The evaluator rejects duplicate IDs, malformed JSON, empty datasets, invalid line collections, and duplicate expected categories.

## Synthetic regression gates

The core fixture can be evaluated with:

```text
python tools/evaluate_detections.py evaluation/labeled_events.jsonl \
  --dataset-kind synthetic \
  --min-precision 1.0 \
  --min-recall 1.0 \
  --min-case-accuracy 1.0 \
  --max-fp 0 \
  --max-fn 0
```

The broader v2.1 corpus can be evaluated with the same strict deterministic gate:

```text
python tools/evaluate_detections.py evaluation/representative_synthetic_v21.jsonl \
  --dataset-kind synthetic \
  --min-precision 1.0 \
  --min-recall 1.0 \
  --min-case-accuracy 1.0 \
  --max-fp 0 \
  --max-fn 0
```

These thresholds are appropriate because both checked-in datasets are deliberately constructed regression fixtures with deterministic expected outputs. Perfect synthetic scores must not be presented as proof of real-world precision or recall.

The report includes 95% Wilson score intervals for precision, recall, and case-level exact-match accuracy. Small perfect samples therefore still have lower confidence bounds below 1.0.

## External independently labeled corpora

Do not commit production logs, credentials, personal data, customer data, or confidential telemetry merely to increase evaluation size. Use appropriately authorized, minimized, and sanitized data according to the organization's data-handling requirements.

Run an external corpus with an explicit provenance statement:

```text
python tools/evaluate_detections.py sanitized_external.jsonl \
  --dataset-kind external \
  --provenance "Source, sampling window, labeling process, sanitization, and reviewer details"
```

`--dataset-kind external` is rejected unless `--provenance` is supplied. The provenance should document the source population, sampling method and time period, labeling/annotation method, sanitization process, class balance, and known exclusions or deployment differences.

External results remain subject to sampling uncertainty, labeling error, class imbalance, prevalence differences, and dataset shift. Wilson intervals quantify binomial sampling uncertainty only; they do not correct those other limitations.

## Building optional release evidence

The generic release preflight can validate `evaluation/external-release-evidence.json` when a future release elects to bind independently reviewed external evidence. That file must not be fabricated or created from either synthetic fixture.

Use the fail-closed generator only after a real, authorized, sanitized, independently labeled external evaluation has been completed for the exact evaluated code commit. The current schema-v2 generator requires explicit source types, collection period, sampling method, known exclusions, provenance, labeling procedure, reviewer identity/role, independent-labeling confirmation, and sanitization confirmation.

```text
python tools/build_external_evidence.py sanitized_external.jsonl \
  --evaluated-commit <40-character-evaluated-code-commit> \
  --provenance "Describe the authorized source population and why it is appropriate" \
  --source-type "auth" \
  --source-type "web" \
  --collection-period "<truthful collection period>" \
  --sampling-method "<truthful sampling method>" \
  --known-exclusion "<truthful known exclusion>" \
  --labeling-procedure "Describe independent labeling, adjudication, and review procedure" \
  --reviewer "Reviewer name or approved review identifier" \
  --reviewer-role "Security Analyst" \
  --independent-labeling \
  --sanitized
```

The generator evaluates the supplied dataset as `external`, derives sample/class/category counts and detection metrics, computes the dataset SHA-256, records per-category metrics, uncertainty, and limitations, and writes the release-preflight schema. It refuses weak or malformed evidence metadata and refuses to overwrite an existing evidence file.

Do not use either checked-in synthetic dataset with this command for release evidence. Do not commit the underlying external telemetry unless the organization has explicitly approved that data for publication. The release evidence manifest should contain metadata, hashes, and aggregate results rather than raw sensitive telemetry.

If the dataset, labels, code, or reviewed metadata change, regenerate the evidence rather than editing metrics or hashes by hand.

## Regression thresholds

Optional gates are available for controlled datasets:

- `--min-precision` between 0 and 1;
- `--min-recall` between 0 and 1;
- `--min-case-accuracy` between 0 and 1;
- `--max-fp` non-negative integer;
- `--max-fn` non-negative integer.

A violated gate returns a non-zero process exit code, making it suitable for CI. Thresholds for independently labeled telemetry should be chosen from documented operational requirements rather than copied from synthetic fixtures.
