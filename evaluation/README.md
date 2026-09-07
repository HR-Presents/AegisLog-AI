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

## Building release evidence

The v1.6 release preflight requires `evaluation/external-release-evidence.json`, but that file must not be fabricated or created from the synthetic fixture. Generate it only after a real, authorized, sanitized, independently labeled external evaluation has been completed for the exact release commit.

Use the fail-closed generator instead of manually typing hashes or metrics:

```text
python tools/build_external_evidence.py sanitized_external.jsonl \
  --evaluated-commit <40-character-release-commit> \
  --provenance "Describe source population, sampling period, sanitization, and exclusions" \
  --labeling-procedure "Describe independent labeling, adjudication, and review procedure" \
  --reviewer "Reviewer name or approved review identifier" \
  --reviewer-role "Security Analyst" \
  --independent-labeling \
  --sanitized
```

The generator evaluates the supplied dataset as `external`, derives the sample count and detection metrics from the evaluator, computes the dataset SHA-256 itself, records uncertainty and limitations, and writes the release-preflight schema. It refuses to generate evidence unless independent labeling and sanitization are explicitly confirmed, rejects malformed commit identifiers or weak narrative metadata, and refuses to overwrite an existing evidence file.

Do not use `evaluation/labeled_events.jsonl` with this command for release evidence. Do not commit the underlying external telemetry unless the organization has explicitly approved that data for publication. The release evidence manifest should contain metadata, hashes, and aggregate results rather than raw sensitive telemetry.

After generation, review the manifest and run the release preflight against the same exact commit. If the dataset, labels, code, or reviewed metadata change, regenerate the evidence rather than editing metrics or hashes by hand.

## Regression thresholds

Optional gates are available for controlled datasets:

- `--min-precision` between 0 and 1;
- `--min-recall` between 0 and 1;
- `--min-case-accuracy` between 0 and 1;
- `--max-fp` non-negative integer;
- `--max-fn` non-negative integer.

A violated gate returns a non-zero process exit code, making it suitable for CI. Thresholds for independently labeled telemetry should be chosen from documented operational requirements rather than copied from the synthetic fixture.
