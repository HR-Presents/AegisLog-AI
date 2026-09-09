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
validate_evidence_binding = release_preflight.validate_evidence_binding
validate_preflight = release_preflight.validate_preflight

EVALUATED_SHA = "a" * 40
RELEASE_SHA = "b" * 40
EVIDENCE_PATH = "evaluation/external-release-evidence.json"


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
        "evaluated_commit": EVALUATED_SHA,
        "sample_count": 100,
        "metrics": {"precision": 0.91, "recall": 0.88, "case_accuracy": 0.89, "false_positives": 4, "false_negatives": 6},
    }


def _write_manifest(tmp_path: Path, payload: dict[str, object] | None = None) -> Path:
    path = tmp_path / "external-release-evidence.json"
    path.write_text(json.dumps(payload or _manifest()), encoding="utf-8")
    return path


def _args(path: Path | None = None) -> Namespace:
    return Namespace(repository="HR-Presents/AegisLog-AI", ref="refs/heads/main", sha=RELEASE_SHA, release_tag="v1.6.0", release_version="1.6.0", confirmation="RELEASE-v1.6.0", external_evidence=path, repository_root=Path("."))


def _mock_valid_commit_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(release_preflight, "_release_commit_shape", lambda release_commit, repository_root: ([EVALUATED_SHA], {EVIDENCE_PATH}))


def test_valid_external_evidence_passes(tmp_path: Path) -> None:
    evidence = validate_external_evidence(_write_manifest(tmp_path))
    assert evidence["dataset_kind"] == "external"
    assert evidence["evaluated_commit"] == EVALUATED_SHA


def test_missing_external_evidence_is_rejected_when_explicitly_requested(tmp_path: Path) -> None:
    with pytest.raises(PreflightError, match="external detection evidence is missing"):
        validate_external_evidence(tmp_path / "missing.json")


def test_synthetic_evidence_is_rejected(tmp_path: Path) -> None:
    payload = _manifest(); payload["dataset_kind"] = "synthetic"
    with pytest.raises(PreflightError, match="dataset_kind"):
        validate_external_evidence(_write_manifest(tmp_path, payload))


def test_malformed_evaluated_commit_is_rejected(tmp_path: Path) -> None:
    payload = _manifest(); payload["evaluated_commit"] = "not-a-sha"
    with pytest.raises(PreflightError, match="evaluated_commit must be"):
        validate_external_evidence(_write_manifest(tmp_path, payload))


def test_non_independent_labeling_is_rejected(tmp_path: Path) -> None:
    payload = _manifest(); payload["independent_labeling"] = False
    with pytest.raises(PreflightError, match="independent_labeling must be true"):
        validate_external_evidence(_write_manifest(tmp_path, payload))


def test_unsanitized_evidence_is_rejected(tmp_path: Path) -> None:
    payload = _manifest(); payload["sanitized"] = False
    with pytest.raises(PreflightError, match="sanitized must be true"):
        validate_external_evidence(_write_manifest(tmp_path, payload))


def test_evidence_binding_accepts_direct_evidence_only_child(monkeypatch: pytest.MonkeyPatch) -> None:
    _mock_valid_commit_shape(monkeypatch)
    validate_evidence_binding(_manifest(), RELEASE_SHA, Path("."))


def test_evidence_binding_rejects_non_direct_ancestor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(release_preflight, "_release_commit_shape", lambda release_commit, repository_root: (["d" * 40], {EVIDENCE_PATH}))
    with pytest.raises(PreflightError, match="direct single-parent child"):
        validate_evidence_binding(_manifest(), RELEASE_SHA, Path("."))


def test_evidence_binding_rejects_merge_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(release_preflight, "_release_commit_shape", lambda release_commit, repository_root: ([EVALUATED_SHA, "d" * 40], {EVIDENCE_PATH}))
    with pytest.raises(PreflightError, match="direct single-parent child"):
        validate_evidence_binding(_manifest(), RELEASE_SHA, Path("."))


def test_evidence_binding_rejects_code_change_with_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(release_preflight, "_release_commit_shape", lambda release_commit, repository_root: ([EVALUATED_SHA], {EVIDENCE_PATH, "src/aegislog/engine.py"}))
    with pytest.raises(PreflightError, match="may differ.*only"):
        validate_evidence_binding(_manifest(), RELEASE_SHA, Path("."))


def test_evidence_binding_rejects_wrong_only_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(release_preflight, "_release_commit_shape", lambda release_commit, repository_root: ([EVALUATED_SHA], {"evaluation/other.json"}))
    with pytest.raises(PreflightError, match="external-release-evidence.json"):
        validate_evidence_binding(_manifest(), RELEASE_SHA, Path("."))


def test_preflight_accepts_release_without_external_evidence() -> None:
    validate_preflight(_args())


def test_preflight_validates_optional_external_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _mock_valid_commit_shape(monkeypatch)
    validate_preflight(_args(_write_manifest(tmp_path)))
