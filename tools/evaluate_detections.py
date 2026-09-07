from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

from aegislog.engine import analyze_lines

SEVERITY_RANK = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
DATASET_KINDS = ("synthetic", "external")


def _safe_div(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> dict[str, float | int]:
    """Return a two-sided Wilson score interval without external statistics dependencies."""
    if total <= 0:
        return {"lower": 0.0, "upper": 0.0, "successes": successes, "total": total}
    proportion = successes / total
    z2 = z * z
    denominator = 1 + z2 / total
    center = (proportion + z2 / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt((proportion * (1 - proportion) / total) + (z2 / (4 * total * total)))
        / denominator
    )
    return {
        "lower": round(max(0.0, center - margin), 4),
        "upper": round(min(1.0, center + margin), 4),
        "successes": successes,
        "total": total,
    }


def _load_cases(path: Path) -> list[dict]:
    cases: list[dict] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                case = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
            if not isinstance(case, dict):
                raise ValueError(f"evaluation row {line_number} must be a JSON object")
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id.strip():
                raise ValueError(f"evaluation row {line_number} must contain a non-empty string id")
            if case_id in seen_ids:
                raise ValueError(f"duplicate evaluation case id: {case_id}")
            seen_ids.add(case_id)
            lines = case.get("lines")
            if not isinstance(lines, list) or not lines or not all(isinstance(item, str) for item in lines):
                raise ValueError(f"evaluation case {case_id} must contain a non-empty list of string lines")
            expected = case.get("expected_categories", [])
            if not isinstance(expected, list) or not all(isinstance(item, str) and item for item in expected):
                raise ValueError(f"evaluation case {case_id} expected_categories must be a list of strings")
            if len(expected) != len(set(expected)):
                raise ValueError(f"evaluation case {case_id} contains duplicate expected_categories")
            label = case.get("label", "unspecified")
            if not isinstance(label, str):
                raise ValueError(f"evaluation case {case_id} label must be a string")
            cases.append(case)
    if not cases:
        raise ValueError("evaluation dataset contains no cases")
    return cases


def evaluate(
    path: Path,
    min_severity: str = "MEDIUM",
    *,
    dataset_kind: str = "synthetic",
    provenance: str | None = None,
) -> dict:
    severity = min_severity.upper()
    if severity not in SEVERITY_RANK:
        raise ValueError(f"unsupported minimum severity: {min_severity}")
    if dataset_kind not in DATASET_KINDS:
        raise ValueError(f"unsupported dataset kind: {dataset_kind}")
    if dataset_kind == "external" and not (provenance and provenance.strip()):
        raise ValueError("external datasets require a non-empty provenance description")

    threshold = SEVERITY_RANK[severity]
    cases = _load_cases(path)
    categories = {category for case in cases for category in case.get("expected_categories", [])}
    rows = []
    totals = {"tp": 0, "fp": 0, "fn": 0}
    per_category = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    exact_cases = 0

    for case in cases:
        expected = set(case.get("expected_categories", []))
        detected = {
            finding.category
            for finding in analyze_lines(case["lines"])
            if SEVERITY_RANK.get(finding.severity.upper(), -1) >= threshold
        }
        categories.update(detected)
        tp = expected & detected
        fp = detected - expected
        fn = expected - detected
        exact_match = expected == detected
        exact_cases += int(exact_match)
        totals["tp"] += len(tp)
        totals["fp"] += len(fp)
        totals["fn"] += len(fn)
        for category in tp:
            per_category[category]["tp"] += 1
        for category in fp:
            per_category[category]["fp"] += 1
        for category in fn:
            per_category[category]["fn"] += 1
        rows.append(
            {
                "id": case["id"],
                "label": case.get("label", "unspecified"),
                "expected": sorted(expected),
                "detected": sorted(detected),
                "exact_match": exact_match,
                "false_positives": sorted(fp),
                "false_negatives": sorted(fn),
            }
        )

    category_metrics = {}
    for category in sorted(categories):
        values = per_category[category]
        precision_total = values["tp"] + values["fp"]
        recall_total = values["tp"] + values["fn"]
        category_metrics[category] = {
            **values,
            "precision": round(_safe_div(values["tp"], precision_total), 4),
            "recall": round(_safe_div(values["tp"], recall_total), 4),
            "precision_ci95": _wilson_interval(values["tp"], precision_total),
            "recall_ci95": _wilson_interval(values["tp"], recall_total),
        }

    precision_total = totals["tp"] + totals["fp"]
    recall_total = totals["tp"] + totals["fn"]
    precision = _safe_div(totals["tp"], precision_total)
    recall = _safe_div(totals["tp"], recall_total)
    exact_accuracy = _safe_div(exact_cases, len(cases))
    if dataset_kind == "synthetic":
        limitations = (
            "Synthetic regression evidence only. It measures consistency against hand-labeled fixtures, not "
            "deployment-specific false-positive rates, real-world detection effectiveness, prevalence, or adversarial robustness."
        )
    else:
        limitations = (
            "External labeled data improves representativeness only to the extent documented by its provenance, sampling, "
            "annotation quality, class balance, and deployment similarity. Confidence intervals quantify sampling uncertainty, "
            "not labeling bias or dataset shift."
        )

    return {
        "dataset": str(path),
        "dataset_kind": dataset_kind,
        "provenance": provenance.strip() if provenance else None,
        "cases": len(cases),
        "minimum_reported_severity": severity,
        "tp": totals["tp"],
        "fp": totals["fp"],
        "fn": totals["fn"],
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "precision_ci95": _wilson_interval(totals["tp"], precision_total),
        "recall_ci95": _wilson_interval(totals["tp"], recall_total),
        "exact_match_cases": exact_cases,
        "case_exact_accuracy": round(exact_accuracy, 4),
        "case_exact_accuracy_ci95": _wilson_interval(exact_cases, len(cases)),
        "per_category": category_metrics,
        "results": rows,
        "limitations": limitations,
    }


def regression_failures(
    report: dict,
    *,
    min_precision: float | None = None,
    min_recall: float | None = None,
    min_case_accuracy: float | None = None,
    max_fp: int | None = None,
    max_fn: int | None = None,
) -> list[str]:
    failures: list[str] = []
    if min_precision is not None and report["precision"] < min_precision:
        failures.append(f"precision {report['precision']:.4f} < required {min_precision:.4f}")
    if min_recall is not None and report["recall"] < min_recall:
        failures.append(f"recall {report['recall']:.4f} < required {min_recall:.4f}")
    if min_case_accuracy is not None and report["case_exact_accuracy"] < min_case_accuracy:
        failures.append(
            f"case exact accuracy {report['case_exact_accuracy']:.4f} < required {min_case_accuracy:.4f}"
        )
    if max_fp is not None and report["fp"] > max_fp:
        failures.append(f"false positives {report['fp']} > allowed {max_fp}")
    if max_fn is not None and report["fn"] > max_fn:
        failures.append(f"false negatives {report['fn']} > allowed {max_fn}")
    return failures


def _unit_interval(value: str) -> float:
    parsed = float(value)
    if not 0.0 <= parsed <= 1.0:
        raise argparse.ArgumentTypeError("value must be between 0 and 1")
    return parsed


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate AegisLog detections against a labeled JSONL dataset.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--min-severity", default="MEDIUM", choices=tuple(SEVERITY_RANK))
    parser.add_argument("--dataset-kind", default="synthetic", choices=DATASET_KINDS)
    parser.add_argument(
        "--provenance",
        help="Required for external datasets; describe source, sampling, labeling, and sanitization provenance.",
    )
    parser.add_argument("--min-precision", type=_unit_interval)
    parser.add_argument("--min-recall", type=_unit_interval)
    parser.add_argument("--min-case-accuracy", type=_unit_interval)
    parser.add_argument("--max-fp", type=_non_negative_int)
    parser.add_argument("--max-fn", type=_non_negative_int)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        report = evaluate(
            args.dataset,
            args.min_severity,
            dataset_kind=args.dataset_kind,
            provenance=args.provenance,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    failures = regression_failures(
        report,
        min_precision=args.min_precision,
        min_recall=args.min_recall,
        min_case_accuracy=args.min_case_accuracy,
        max_fp=args.max_fp,
        max_fn=args.max_fn,
    )
    report["regression_gate"] = {"passed": not failures, "failures": failures}

    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"cases={report['cases']} kind={report['dataset_kind']} precision={report['precision']:.4f} "
            f"recall={report['recall']:.4f} exact_accuracy={report['case_exact_accuracy']:.4f} "
            f"fp={report['fp']} fn={report['fn']}"
        )
        print(
            "precision_ci95="
            f"[{report['precision_ci95']['lower']:.4f}, {report['precision_ci95']['upper']:.4f}] "
            "recall_ci95="
            f"[{report['recall_ci95']['lower']:.4f}, {report['recall_ci95']['upper']:.4f}]"
        )
        for category, metrics in report["per_category"].items():
            print(
                f"{category}: precision={metrics['precision']:.4f} recall={metrics['recall']:.4f} "
                f"tp={metrics['tp']} fp={metrics['fp']} fn={metrics['fn']}"
            )
        print(f"limitations: {report['limitations']}")
        if failures:
            for failure in failures:
                print(f"REGRESSION: {failure}")
        else:
            print("regression_gate=passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
