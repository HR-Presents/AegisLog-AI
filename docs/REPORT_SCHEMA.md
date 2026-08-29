# JSON report schema (V0.2)

Reports contain:

- `source`: analyzed file path
- `lines`: number of lines read
- `findings`: deterministic rule/correlation findings
- `anomalies`: local anomaly scores
- `incidents`: category-correlated investigation groups

The schema is pre-1.0 and may change. Reports can contain sensitive evidence even after automatic redaction, so treat generated report files with the same care as source logs.
