from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.build_external_evidence import EvidenceError, build_evidence, main
from tools.release_preflight import validate_external_evidence


COMMIT = "a" * 40
PROVENANCE = "Sanitized representative sample from an authorized staging environment."
LABELING = "Two analysts labeled cases independently before adjudication and review."


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


def test_generator_derives_metrics_hash_and_preflight_compatible_schema(tmp_path):
    dataset = _dataset(tmp_path)
    evidence = build_evidence(
        dataset,
        evaluated_commit=COMMIT,
        provenance=PROVENANCE,
        labeling_procedure=LABELING,
        reviewer="Reviewer A",
        reviewer_role="Security Analyst",
        independent_labeling=True,
        sanitized=True,
    )

    assert evidence["dataset_kind"] == "external"
    assert evidence["sample_count"] == 2
    assert evidence["dataset_sha256"] == hashlib.sha256(dataset.read_bytes()).hexdigest()
    assert evidence["evaluated_commit"] == COMMIT
    assert evidence["metrics"] == {
        "precision": 1.0,
        "recall": 1.0,
        "case_accuracy": 1.0,
        "false_positives": 0,
        "false_negatives": 0,
    }

    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    assert validate_external_evidence(evidence_path, COMMIT)["dataset_sha256"] == evidence["dataset_sha256"]


def test_generator_requires_explicit_independent_labeling_and_sanitization(tmp_path):
    dataset = _dataset(tmp_path)
    common = dict(
        evaluated_commit=COMMIT,
        provenance=PROVENANCE,
        labeling_procedure=LABELING,
        reviewer="Reviewer A",
        reviewer_role="Security Analyst",
    )

    with pytest.raises(EvidenceError, match="independent_labeling"):
        build_evidence(dataset, independent_labeling=False, sanitized=True, **common)
    with pytest.raises(EvidenceError, match="sanitized"):
        build_evidence(dataset, independent_labeling=True, sanitized=False, **common)


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
            "--independent-labeling",
            "--sanitized",
            "--output",
            str(output),
        ]
    )

    assert result == 2
    assert output.read_text(encoding="utf-8") == '{"existing": true}\n'
