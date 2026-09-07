from __future__ import annotations

import importlib.util
import json
from argparse import Namespace
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "release_preflight.py"
SPEC = importlib.util.spec_from_file_location("release_preflight", MODULE_PATH)
assert SPEC and SPEC.loader
release_preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_preflight)

PreflightError = release_preflight.PreflightError
validate_external_evidence = release_preflight.validate_external_evidence
validate_preflight = release_preflight.validate_preflight

SHA = "a" * 40
THUMBPRINT = "B" * 40


def _manifest() -> dict[str, object]:
    return {
        "schema_version": 1,
        "dataset_kind": "external",
        "provenance": "Authorized representative security telemetry sample.",
        "labeling_procedure": "Independently reviewed labels using documented criteria.",
        "reviewer": "Security Reviewer",
        "reviewer_role": "Detection Engineering",
        "independent_labeling": True,
        "sanitized": True,
        "dataset_sha256": "c" * 64,
        "evaluated_commit": SHA,
        "sample_count": 100,
        "metrics": {
            "precision": 0.91,
            "recall": 0.88,
            "case_accuracy": 0.89,
            "false_positives": 4,
            "false_negatives": 6,
        },
    }


def _write_manifest(tmp_path: Path, payload: dict[str, object] | None = None) -> Path:
    path = tmp_path / "external-release-evidence.json"
    path.write_text(json.dumps(payload or _manifest()), encoding="utf-8")
    return path


def _args(path: Path) -> Namespace:
    return Namespace(
        repository="HR-Presents/AegisLog-AI",
        ref="refs/heads/main",
        sha=SHA,
        release_tag="v1.6.0",
        release_version="1.6.0",
        confirmation="RELEASE-v1.6.0",
        signing_thumbprint=THUMBPRINT,
        timestamp_url="https://timestamp.example.test/rfc3161",
        external_evidence=path,
    )


def test_valid_external_evidence_passes(tmp_path: Path) -> None:
    path = _write_manifest(tmp_path)
    evidence = validate_external_evidence(path, SHA)
    assert evidence["dataset_kind"] == "external"


def test_missing_external_evidence_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(PreflightError, match="evidence is required but missing"):
        validate_external_evidence(tmp_path / "missing.json", SHA)


def test_synthetic_evidence_is_rejected(tmp_path: Path) -> None:
    payload = _manifest()
    payload["dataset_kind"] = "synthetic"
    with pytest.raises(PreflightError, match="dataset_kind"):
        validate_external_evidence(_write_manifest(tmp_path, payload), SHA)


def test_evidence_for_different_commit_is_rejected(tmp_path: Path) -> None:
    payload = _manifest()
    payload["evaluated_commit"] = "d" * 40
    with pytest.raises(PreflightError, match="does not match the release commit"):
        validate_external_evidence(_write_manifest(tmp_path, payload), SHA)


def test_non_independent_labeling_is_rejected(tmp_path: Path) -> None:
    payload = _manifest()
    payload["independent_labeling"] = False
    with pytest.raises(PreflightError, match="independent_labeling must be true"):
        validate_external_evidence(_write_manifest(tmp_path, payload), SHA)


def test_unsanitized_evidence_is_rejected(tmp_path: Path) -> None:
    payload = _manifest()
    payload["sanitized"] = False
    with pytest.raises(PreflightError, match="sanitized must be true"):
        validate_external_evidence(_write_manifest(tmp_path, payload), SHA)


def test_preflight_rejects_http_timestamp_url(tmp_path: Path) -> None:
    args = _args(_write_manifest(tmp_path))
    args.timestamp_url = "http://timestamp.example.test"
    with pytest.raises(PreflightError, match="credential-free HTTPS"):
        validate_preflight(args)


def test_preflight_rejects_malformed_thumbprint(tmp_path: Path) -> None:
    args = _args(_write_manifest(tmp_path))
    args.signing_thumbprint = "1234"
    with pytest.raises(PreflightError, match="40 hexadecimal"):
        validate_preflight(args)


def test_preflight_accepts_complete_release_context(tmp_path: Path) -> None:
    validate_preflight(_args(_write_manifest(tmp_path)))
