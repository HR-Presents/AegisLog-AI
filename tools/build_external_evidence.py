from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from evaluate_detections import evaluate

GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class EvidenceError(ValueError):
    pass


def _meaningful(value: str, field: str, minimum: int = 2) -> str:
    cleaned = value.strip()
    if len(cleaned) < minimum:
        raise EvidenceError(f"{field} must contain at least {minimum} characters")
    return cleaned


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

    report = evaluate(
        dataset,
        min_severity,
        dataset_kind="external",
        provenance=provenance_text,
    )
    dataset_sha256 = hashlib.sha256(dataset.read_bytes()).hexdigest()

    return {
        "schema_version": 1,
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
        "metrics": {
            "precision": report["precision"],
            "recall": report["recall"],
            "case_accuracy": report["case_exact_accuracy"],
            "false_positives": report["fp"],
            "false_negatives": report["fn"],
        },
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
            min_severity=args.min_severity,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ValueError, EvidenceError) as exc:
        print(f"external evidence generation failed: {exc}", file=sys.stderr)
        return 2

    print(f"external evidence written: {args.output}")
    print(f"dataset_sha256={evidence['dataset_sha256']}")
    print(f"evaluated_commit={evidence['evaluated_commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
