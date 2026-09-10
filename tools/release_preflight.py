from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXTERNAL_EVIDENCE_REPO_PATH = "evaluation/external-release-evidence.json"


class PreflightError(ValueError):
    pass


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PreflightError(f"{field} must be a non-empty string")
    return value.strip()


def _require_bool(value: object, field: str) -> bool:
    if value is not True:
        raise PreflightError(f"{field} must be true")
    return True


def _require_metric(value: object, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise PreflightError(f"{field} must be numeric")
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise PreflightError(f"{field} must be between 0 and 1")
    return number


def _require_non_negative_int(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise PreflightError(f"{field} must be a non-negative integer")
    return value


def _validate_ci(value: object, field: str) -> None:
    if not isinstance(value, dict):
        raise PreflightError(f"{field} must be a JSON object")
    lower = _require_metric(value.get("lower"), f"{field}.lower")
    upper = _require_metric(value.get("upper"), f"{field}.upper")
    if lower > upper:
        raise PreflightError(f"{field}.lower must not exceed upper")
    successes = _require_non_negative_int(value.get("successes"), f"{field}.successes")
    total = _require_non_negative_int(value.get("total"), f"{field}.total")
    if successes > total:
        raise PreflightError(f"{field}.successes must not exceed total")


def _validate_dataset_profile(value: object) -> None:
    if not isinstance(value, dict):
        raise PreflightError("dataset_profile must be a JSON object")
    source_types = value.get("source_types")
    if not isinstance(source_types, list) or not source_types:
        raise PreflightError("dataset_profile.source_types must be a non-empty list")
    cleaned: list[str] = []
    for item in source_types:
        cleaned.append(_require_text(item, "dataset_profile.source_types[]"))
    if len(cleaned) != len(set(cleaned)):
        raise PreflightError("dataset_profile.source_types must contain unique values")
    collection_period = _require_text(value.get("collection_period"), "dataset_profile.collection_period")
    sampling_method = _require_text(value.get("sampling_method"), "dataset_profile.sampling_method")
    exclusions = _require_text(value.get("known_exclusions"), "dataset_profile.known_exclusions")
    if len(collection_period) < 8:
        raise PreflightError("dataset_profile.collection_period must contain at least 8 characters")
    if len(sampling_method) < 20:
        raise PreflightError("dataset_profile.sampling_method must contain at least 20 characters")
    if len(exclusions) < 4:
        raise PreflightError("dataset_profile.known_exclusions must contain at least 4 characters")


def _validate_class_balance(value: object, sample_count: int) -> None:
    if not isinstance(value, dict):
        raise PreflightError("class_balance must be a JSON object")
    benign = _require_non_negative_int(value.get("benign_cases"), "class_balance.benign_cases")
    positive = _require_non_negative_int(value.get("positive_cases"), "class_balance.positive_cases")
    if benign + positive != sample_count:
        raise PreflightError("class_balance benign_cases + positive_cases must equal sample_count")
    category_counts = value.get("expected_category_case_counts")
    if not isinstance(category_counts, dict):
        raise PreflightError("class_balance.expected_category_case_counts must be a JSON object")
    for category, count in category_counts.items():
        _require_text(category, "class_balance.expected_category_case_counts key")
        if _require_non_negative_int(count, f"class_balance.expected_category_case_counts.{category}") <= 0:
            raise PreflightError("expected category case counts must be positive integers")


def _validate_per_category_metrics(value: object) -> None:
    if not isinstance(value, dict):
        raise PreflightError("per_category_metrics must be a JSON object")
    for category, metrics in value.items():
        _require_text(category, "per_category_metrics key")
        if not isinstance(metrics, dict):
            raise PreflightError(f"per_category_metrics.{category} must be a JSON object")
        for field in ("tp", "fp", "fn"):
            _require_non_negative_int(metrics.get(field), f"per_category_metrics.{category}.{field}")
        _require_metric(metrics.get("precision"), f"per_category_metrics.{category}.precision")
        _require_metric(metrics.get("recall"), f"per_category_metrics.{category}.recall")
        _validate_ci(metrics.get("precision_ci95"), f"per_category_metrics.{category}.precision_ci95")
        _validate_ci(metrics.get("recall_ci95"), f"per_category_metrics.{category}.recall_ci95")


def validate_external_evidence(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise PreflightError(f"external detection evidence is missing: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreflightError(f"external evidence is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise PreflightError("external evidence must be a JSON object")
    if payload.get("schema_version") != 2:
        raise PreflightError("external evidence schema_version must be 2")
    if payload.get("dataset_kind") != "external":
        raise PreflightError("external evidence dataset_kind must be 'external'")
    provenance = _require_text(payload.get("provenance"), "provenance")
    labeling = _require_text(payload.get("labeling_procedure"), "labeling_procedure")
    reviewer = _require_text(payload.get("reviewer"), "reviewer")
    reviewer_role = _require_text(payload.get("reviewer_role"), "reviewer_role")
    _require_bool(payload.get("independent_labeling"), "independent_labeling")
    _require_bool(payload.get("sanitized"), "sanitized")
    dataset_sha256 = _require_text(payload.get("dataset_sha256"), "dataset_sha256").lower()
    if not SHA256_RE.fullmatch(dataset_sha256):
        raise PreflightError("dataset_sha256 must be 64 lowercase hexadecimal characters")
    evaluated_commit = _require_text(payload.get("evaluated_commit"), "evaluated_commit").lower()
    if not GIT_SHA_RE.fullmatch(evaluated_commit):
        raise PreflightError("evaluated_commit must be a lowercase 40-character Git SHA")
    sample_count = payload.get("sample_count")
    if not isinstance(sample_count, int) or isinstance(sample_count, bool) or sample_count <= 0:
        raise PreflightError("sample_count must be a positive integer")
    minimum_severity = _require_text(payload.get("minimum_reported_severity"), "minimum_reported_severity")
    if minimum_severity not in {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        raise PreflightError("minimum_reported_severity is not supported")

    _validate_dataset_profile(payload.get("dataset_profile"))
    _validate_class_balance(payload.get("class_balance"), sample_count)

    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        raise PreflightError("metrics must be a JSON object")
    _require_metric(metrics.get("precision"), "metrics.precision")
    _require_metric(metrics.get("recall"), "metrics.recall")
    _require_metric(metrics.get("case_accuracy"), "metrics.case_accuracy")
    for field in ("false_positives", "false_negatives"):
        _require_non_negative_int(metrics.get(field), f"metrics.{field}")

    _validate_per_category_metrics(payload.get("per_category_metrics"))
    uncertainty = payload.get("uncertainty")
    if not isinstance(uncertainty, dict):
        raise PreflightError("uncertainty must be a JSON object")
    _validate_ci(uncertainty.get("precision_ci95"), "uncertainty.precision_ci95")
    _validate_ci(uncertainty.get("recall_ci95"), "uncertainty.recall_ci95")
    _validate_ci(uncertainty.get("case_accuracy_ci95"), "uncertainty.case_accuracy_ci95")
    _require_text(payload.get("limitations"), "limitations")

    if len(provenance) < 20:
        raise PreflightError("provenance must contain at least 20 characters")
    if len(labeling) < 20:
        raise PreflightError("labeling_procedure must contain at least 20 characters")
    if len(reviewer) < 2 or len(reviewer_role) < 2:
        raise PreflightError("reviewer and reviewer_role must be meaningful")
    return payload


def _release_commit_shape(release_commit: str, repository_root: Path) -> tuple[list[str], set[str]]:
    try:
        parent_result = subprocess.run(["git", "show", "--format=%P", "--no-patch", release_commit], cwd=repository_root, check=True, capture_output=True, text=True)
        files_result = subprocess.run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", release_commit], cwd=repository_root, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PreflightError("unable to inspect release commit ancestry for external evidence binding") from exc
    parents = parent_result.stdout.strip().split()
    changed_files = {line.strip() for line in files_result.stdout.splitlines() if line.strip()}
    return parents, changed_files


def validate_evidence_binding(payload: dict[str, object], release_commit: str, repository_root: Path) -> None:
    evaluated_commit = str(payload["evaluated_commit"])
    parents, changed_files = _release_commit_shape(release_commit, repository_root)
    if parents != [evaluated_commit]:
        raise PreflightError("release commit must be a direct single-parent child of evaluated_commit")
    if changed_files != {EXTERNAL_EVIDENCE_REPO_PATH}:
        raise PreflightError("release commit may differ from evaluated_commit only by " f"{EXTERNAL_EVIDENCE_REPO_PATH}")


def validate_preflight(args: argparse.Namespace) -> None:
    if args.repository != "HR-Presents/AegisLog-AI":
        raise PreflightError("release must run in HR-Presents/AegisLog-AI")
    if args.ref != "refs/heads/main":
        raise PreflightError("release must be dispatched from refs/heads/main")
    if not GIT_SHA_RE.fullmatch(args.sha):
        raise PreflightError("release SHA must be a lowercase 40-character Git SHA")
    if args.release_tag != f"v{args.release_version}":
        raise PreflightError("release tag/version mismatch")
    if args.confirmation != f"RELEASE-{args.release_tag}":
        raise PreflightError("release confirmation does not match release tag")
    if args.external_evidence is not None:
        evidence = validate_external_evidence(args.external_evidence)
        validate_evidence_binding(evidence, args.sha, args.repository_root)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fail-closed AegisLog release preflight")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--confirmation", required=True)
    parser.add_argument(
        "--external-evidence",
        type=Path,
        help="Optional independently reviewed external benchmark evidence. Not required for release.",
    )
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        validate_preflight(args)
    except PreflightError as exc:
        print(f"release preflight failed: {exc}", file=sys.stderr)
        return 2
    print("release preflight passed")
    print(f"release_sha={args.sha}")
    if args.external_evidence is not None:
        evidence_bytes = args.external_evidence.read_bytes()
        evidence_hash = hashlib.sha256(evidence_bytes).hexdigest()
        print(f"external_evidence_sha256={evidence_hash}")
    else:
        print("external_evidence=not-required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
