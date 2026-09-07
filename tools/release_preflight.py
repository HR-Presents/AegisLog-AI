from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
THUMBPRINT_RE = re.compile(r"^[0-9A-F]{40}$")


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


def validate_external_evidence(path: Path, expected_commit: str) -> dict[str, object]:
    if not path.is_file():
        raise PreflightError(
            f"external detection evidence is required but missing: {path}"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreflightError(f"external evidence is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise PreflightError("external evidence must be a JSON object")

    if payload.get("schema_version") != 1:
        raise PreflightError("external evidence schema_version must be 1")
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
    if evaluated_commit != expected_commit:
        raise PreflightError(
            "external evidence evaluated_commit does not match the release commit"
        )

    sample_count = payload.get("sample_count")
    if not isinstance(sample_count, int) or isinstance(sample_count, bool) or sample_count <= 0:
        raise PreflightError("sample_count must be a positive integer")

    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        raise PreflightError("metrics must be a JSON object")
    _require_metric(metrics.get("precision"), "metrics.precision")
    _require_metric(metrics.get("recall"), "metrics.recall")
    _require_metric(metrics.get("case_accuracy"), "metrics.case_accuracy")

    for field in ("false_positives", "false_negatives"):
        value = metrics.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise PreflightError(f"metrics.{field} must be a non-negative integer")

    # Require enough narrative detail to make a one-word placeholder impossible.
    if len(provenance) < 20:
        raise PreflightError("provenance must contain at least 20 characters")
    if len(labeling) < 20:
        raise PreflightError("labeling_procedure must contain at least 20 characters")
    if len(reviewer) < 2 or len(reviewer_role) < 2:
        raise PreflightError("reviewer and reviewer_role must be meaningful")

    return payload


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

    thumbprint = args.signing_thumbprint.replace(" ", "").upper()
    if not THUMBPRINT_RE.fullmatch(thumbprint):
        raise PreflightError(
            "Windows signing thumbprint must be exactly 40 hexadecimal characters"
        )

    parsed = urlparse(args.timestamp_url)
    if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise PreflightError(
            "Windows timestamp URL must be credential-free HTTPS with a hostname"
        )

    validate_external_evidence(args.external_evidence, args.sha)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fail-closed AegisLog release preflight")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--confirmation", required=True)
    parser.add_argument("--signing-thumbprint", required=True)
    parser.add_argument("--timestamp-url", required=True)
    parser.add_argument("--external-evidence", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        validate_preflight(args)
    except PreflightError as exc:
        print(f"release preflight failed: {exc}", file=sys.stderr)
        return 2
    evidence_bytes = args.external_evidence.read_bytes()
    evidence_hash = hashlib.sha256(evidence_bytes).hexdigest()
    print("release preflight passed")
    print(f"release_sha={args.sha}")
    print(f"external_evidence_sha256={evidence_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
