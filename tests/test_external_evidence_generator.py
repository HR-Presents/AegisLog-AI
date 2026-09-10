from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

EVAL_SPEC = importlib.util.spec_from_file_location("evaluate_detections", TOOLS / "evaluate_detections.py")
assert EVAL_SPEC and EVAL_SPEC.loader
evaluate_detections = importlib.util.module_from_spec(EVAL_SPEC)
sys.modules["evaluate_detections"] = evaluate_detections
EVAL_SPEC.loader.exec_module(evaluate_detections)

GEN_SPEC = importlib.util.spec_from_file_location("build_external_evidence", TOOLS / "build_external_evidence.py")
assert GEN_SPEC and GEN_SPEC.loader
build_external_evidence = importlib.util.module_from_spec(GEN_SPEC)
GEN_SPEC.loader.exec_module(build_external_evidence)

PREFLIGHT_SPEC = importlib.util.spec_from_file_location("release_preflight", TOOLS / "release_preflight.py")
assert PREFLIGHT_SPEC and PREFLIGHT_SPEC.loader
release_preflight = importlib.util.module_from_spec(PREFLIGHT_SPEC)
PREFLIGHT_SPEC.loader.exec_module(release_preflight)

EvidenceError = build_external_evidence.EvidenceError
build_evidence = build_external_evidence.build_evidence
main = build_external_evidence.main
validate_external_evidence = release_preflight.validate_external_evidence

COMMIT = "a" * 40
PROVENANCE = "Sanitized representative sample from an authorized staging environment."
LABELING = "Two analysts labeled cases independently before adjudication and review."
COLLECTION_PERIOD = "2026-08-01 through 2026-08-31 UTC"
SAMPLING_METHOD = "Stratified sampling across benign and reviewed security-event cases."
KNOWN_EXCLUSIONS = "Cloud control-plane and endpoint EDR telemetry were not included."
SOURCE_TYPES = ["linux-auth", "application"]


def _dataset(tmp_path: Path) -> Path:
    path = tmp_path / "external.jsonl"
    rows = [
        {
            "id": "auth-positive",
            "label": "repeated authentication failures",
            "lines": [
                f"2026-09-07T10:00:0{i}Z sshd: Failed password for root from 203.0.113.7 port {2200 + i}"
                for i in range(6)
            ],
            "expected_categories": ["authentication"],
        },
        {
            "id": "benign",
            "label": "benign service message",
            "lines": ["2026-09-07T10:01:00Z app: service started normally"],
            "expected_categories": [],
        },
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return path


def _build(dataset: Path, **overrides):
    values = dict(
        evaluated_commit=COMMIT,
        provenance=PROVENANCE,
        labeling_procedure=LABELING,
        reviewer="Reviewer A",
        reviewer_role="Security Analyst",
        independent_labeling=True,
        sanitized=True,
        source_types=SOURCE_TYPES,
        collection_period=COLLECTION_PERIOD,
        sampling_method=SAMPLING_METHOD,
        known_exclusions=KNOWN_EXCLUSIONS,
    )
    values.update(overrides)
    return build_evidence(dataset, **values)


def test_generator_derives_metrics_profile_hash_and_preflight_compatible_schema(tmp_path):
    dataset = _dataset(tmp_path)
    evidence = _build(dataset)

    assert evidence["schema_version"] == 2
    assert evidence["dataset_kind"] == "external"
    assert evidence["sample_count"] == 2
    assert evidence["dataset_sha256"] == hashlib.sha256(dataset.read_bytes()).hexdigest()
    assert evidence["evaluated_commit"] == COMMIT
    assert evidence["dataset_profile"] == {
        "source_types": ["application", "linux-auth"],
        "collection_period": COLLECTION_PERIOD,
        "sampling_method": SAMPLING_METHOD,
        "known_exclusions": KNOWN_EXCLUSIONS,
    }
    assert evidence["class_balance"] == {
        "benign_cases": 1,
        "positive_cases": 1,
        "expected_category_case_counts": {"authentication": 1},
    }
    assert evidence["metrics"] == {
        "precision": 1.0,
        "recall": 1.0,
        "case_accuracy": 1.0,
        "false_positives": 0,
        "false_negatives": 0,
    }
    category = evidence["per_category_metrics"]["authentication"]
    assert category["precision"] == 1.0
    assert category["recall"] == 1.0
    assert "precision_ci95" in category
    assert "case_accuracy_ci95" in evidence["uncertainty"]

    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    assert validate_external_evidence(evidence_path)["dataset_sha256"] == evidence["dataset_sha256"]


def test_generator_requires_explicit_independent_labeling_and_sanitization(tmp_path):
    dataset = _dataset(tmp_path)
    with pytest.raises(EvidenceError, match="independent_labeling"):
        _build(dataset, independent_labeling=False)
    with pytest.raises(EvidenceError, match="sanitized"):
        _build(dataset, sanitized=False)


def test_generator_requires_auditable_dataset_profile(tmp_path):
    dataset = _dataset(tmp_path)
    with pytest.raises(EvidenceError, match="source_type"):
        _build(dataset, source_types=[])
    with pytest.raises(EvidenceError, match="unique"):
        _build(dataset, source_types=["linux-auth", "linux-auth"])
    with pytest.raises(EvidenceError, match="sampling_method"):
        _build(dataset, sampling_method="random")
    with pytest.raises(EvidenceError, match="known_exclusions"):
        _build(dataset, known_exclusions="")


def test_cli_refuses_to_overwrite_existing_release_evidence(tmp_path):
    dataset = _dataset(tmp_path)
    output = tmp_path / "external-release-evidence.json"
    output.write_text('{"existing": true}\n', encoding="utf-8")

    result = main(
        [
            str(dataset),
            "--evaluated-commit",
            COMMIT,
            "--provenance",
            PROVENANCE,
            "--labeling-procedure",
            LABELING,
            "--reviewer",
            "Reviewer A",
            "--reviewer-role",
            "Security Analyst",
            "--source-type",
            "linux-auth",
            "--source-type",
            "application",
            "--collection-period",
            COLLECTION_PERIOD,
            "--sampling-method",
            SAMPLING_METHOD,
            "--known-exclusions",
            KNOWN_EXCLUSIONS,
            "--independent-labeling",
            "--sanitized",
            "--output",
            str(output),
        ]
    )

    assert result == 2
    assert output.read_text(encoding="utf-8") == '{"existing": true}\n'
