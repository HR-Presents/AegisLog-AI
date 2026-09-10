from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    from tools.evaluate_detections import evaluate
except ModuleNotFoundError:  # Direct script execution from tools/.
    from evaluate_detections import evaluate

GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class EvidenceError(ValueError):
    pass


def _meaningful(value: str, field: str, minimum: int = 2) -> str:
    cleaned = value.strip()
    if len(cleaned) < minimum:
        raise EvidenceError(f"{field} must contain at least {minimum} characters")
    return cleaned


def _source_types(values: list[str]) -> list[str]:
    cleaned = [_meaningful(value, "source_type") for value in values]
    if not cleaned:
        raise EvidenceError("at least one source_type is required")
    if len(cleaned) != len(set(cleaned)):
        raise EvidenceError("source_type values must be unique")
    return sorted(cleaned)


def _class_balance(report: dict[str, object]) -> dict[str, object]:
    rows = report.get("results")
    if not isinstance(rows, list):
        raise EvidenceError("evaluation report did not contain result rows")

    benign_cases = 0
    positive_cases = 0
    category_counts: Counter[str] = Counter()
    for row in rows:
        if not isinstance(row, dict):
            raise EvidenceError("evaluation result row must be an object")
        expected = row.get("expected")
        if not isinstance(expected, list) or not all(isinstance(item, str) and item for item in expected):
            raise EvidenceError("evaluation result row has invalid expected categories")
        if expected:
            positive_cases += 1
            category_counts.update(expected)
        else:
            benign_cases += 1

    return {
        "benign_cases": benign_cases,
        "positive_cases": positive_cases,
        "expected_category_case_counts": dict(sorted(category_counts.items())),
    }


def build_evidence(
    dataset: Path,
    *,
    evaluated_commit: str,
    provenance: str,
    labeling_procedure: str,
    reviewer: str,
    reviewer_role: str,
    independent_labeling: bool,
    sanitized: bool,
    source_types: list[str],
    collection_period: str,
    sampling_method: str,
    known_exclusions: str,
    min_severity: str = "MEDIUM",
) -> dict[str, object]:
    if not dataset.is_file():
        raise EvidenceError(f"external dataset does not exist: {dataset}")
    if not GIT_SHA_RE.fullmatch(evaluated_commit):
        raise EvidenceError("evaluated_commit must be a lowercase 40-character Git SHA")
    if not independent_labeling:
        raise EvidenceError("independent_labeling must be explicitly confirmed")
    if not sanitized:
        raise EvidenceError("sanitized must be explicitly confirmed before release evidence is generated")

    provenance_text = _meaningful(provenance, "provenance", 20)
    labeling_text = _meaningful(labeling_procedure, "labeling_procedure", 20)
    reviewer_text = _meaningful(reviewer, "reviewer")
    reviewer_role_text = _meaningful(reviewer_role, "reviewer_role")
    profile = {
        "source_types": _source_types(source_types),
        "collection_period": _meaningful(collection_period, "collection_period", 8),
        "sampling_method": _meaningful(sampling_method, "sampling_method", 20),
        "known_exclusions": _meaningful(known_exclusions, "known_exclusions", 4),
    }

    report = evaluate(
        dataset,
        min_severity,
        dataset_kind="external",
        provenance=provenance_text,
    )
    dataset_sha256 = hashlib.sha256(dataset.read_bytes()).hexdigest()

    return {
        "schema_version": 2,
        "dataset_kind": "external",
        "provenance": provenance_text,
        "labeling_procedure": labeling_text,
        "reviewer": reviewer_text,
        "reviewer_role": reviewer_role_text,
        "independent_labeling": True,
        "sanitized": True,
        "dataset_sha256": dataset_sha256,
        "evaluated_commit": evaluated_commit,
        "sample_count": report["cases"],
        "minimum_reported_severity": report["minimum_reported_severity"],
        "dataset_profile": profile,
        "class_balance": _class_balance(report),
        "metrics": {
            "precision": report["precision"],
            "recall": report["recall"],
            "case_accuracy": report["case_exact_accuracy"],
            "false_positives": report["fp"],
            "false_negatives": report["fn"],
        },
        "per_category_metrics": report["per_category"],
        "uncertainty": {
            "precision_ci95": report["precision_ci95"],
            "recall_ci95": report["recall_ci95"],
            "case_accuracy_ci95": report["case_exact_accuracy_ci95"],
        },
        "limitations": report["limitations"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate reviewed external detection evidence from an actual labeled dataset."
    )
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--evaluated-commit", required=True)
    parser.add_argument("--provenance", required=True)
    parser.add_argument("--labeling-procedure", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reviewer-role", required=True)
    parser.add_argument(
        "--source-type",
        action="append",
        required=True,
        dest="source_types",
        help="Log/source type represented by the dataset. Repeat for multiple types.",
    )
    parser.add_argument("--collection-period", required=True)
    parser.add_argument("--sampling-method", required=True)
    parser.add_argument("--known-exclusions", required=True)
    parser.add_argument("--independent-labeling", action="store_true")
    parser.add_argument("--sanitized", action="store_true")
    parser.add_argument("--min-severity", default="MEDIUM")
    parser.add_argument("--output", type=Path, default=Path("evaluation/external-release-evidence.json"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            raise EvidenceError(f"refusing to overwrite existing evidence file: {args.output}")
        evidence = build_evidence(
            args.dataset,
            evaluated_commit=args.evaluated_commit,
            provenance=args.provenance,
            labeling_procedure=args.labeling_procedure,
            reviewer=args.reviewer,
            reviewer_role=args.reviewer_role,
            independent_labeling=args.independent_labeling,
            sanitized=args.sanitized,
            source_types=args.source_types,
            collection_period=args.collection_period,
            sampling_method=args.sampling_method,
            known_exclusions=args.known_exclusions,
            min_severity=args.min_severity,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"external evidence generation failed: {exc}", file=sys.stderr)
        return 2

    print(f"external evidence written: {args.output}")
    print(f"dataset_sha256={evidence['dataset_sha256']}")
    print(f"evaluated_commit={evidence['evaluated_commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
