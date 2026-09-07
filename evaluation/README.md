# Detection evaluation

AegisLog's checked-in `labeled_events.jsonl` is a small synthetic regression fixture. It exists to catch deterministic detection changes; it is not evidence of deployment-specific security effectiveness.

## Dataset format

Each non-empty JSONL row must be an object with:

- `id`: unique, non-empty string;
- `lines`: non-empty list of log-event strings;
- `expected_categories`: list of expected detection categories (may be empty);
- `label`: optional descriptive string.

The evaluator rejects duplicate IDs, malformed JSON, empty datasets, invalid line collections, and duplicate expected categories.

## Synthetic regression gate

CI runs:

```text
python tools/evaluate_detections.py evaluation/labeled_events.jsonl \
  --dataset-kind synthetic \
  --min-precision 1.0 \
  --min-recall 1.0 \
  --min-case-accuracy 1.0 \
  --max-fp 0 \
  --max-fn 0
```

These strict thresholds are appropriate for the tiny checked-in regression fixture because the expected output is intentionally deterministic. They must not be presented as proof of real-world precision or recall.

The report includes 95% Wilson score intervals for precision, recall, and case-level exact-match accuracy. Small perfect samples therefore still have lower confidence bounds below 1.0.

## External independently labeled corpora

Do not commit production logs, credentials, personal data, customer data, or confidential telemetry merely to increase evaluation size. Use appropriately authorized, minimized, and sanitized data according to the organization's data-handling requirements.

Run an external corpus with an explicit provenance statement:

```text
python tools/evaluate_detections.py sanitized_external.jsonl \
  --dataset-kind external \
  --provenance "Source, sampling window, labeling process, sanitization, and reviewer details"
```

`--dataset-kind external` is rejected unless `--provenance` is supplied. The provenance should document at minimum the source population, sampling method and time period, labeling/annotation method, sanitization process, class balance, and any known exclusions or deployment differences.

External results remain subject to sampling uncertainty, labeling error, class imbalance, prevalence differences, and dataset shift. Wilson intervals quantify binomial sampling uncertainty only; they do not correct those other limitations.

## Regression thresholds

Optional gates are available for controlled datasets:

- `--min-precision` between 0 and 1;
- `--min-recall` between 0 and 1;
- `--min-case-accuracy` between 0 and 1;
- `--max-fp` non-negative integer;
- `--max-fn` non-negative integer.

A violated gate returns a non-zero process exit code, making it suitable for CI. Thresholds for independently labeled telemetry should be chosen from documented operational requirements rather than copied from the synthetic fixture.
