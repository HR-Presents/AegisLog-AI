from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation" / "representative_synthetic_v21.jsonl"
MODULE_PATH = ROOT / "tools" / "evaluate_detections.py"
SPEC = importlib.util.spec_from_file_location("evaluate_detections_representative", MODULE_PATH)
assert SPEC and SPEC.loader
evaluate_detections = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluate_detections)


def test_representative_synthetic_corpus_has_broader_coverage() -> None:
    cases = evaluate_detections._load_cases(DATASET)
    benign = [case for case in cases if not case["expected_categories"]]
    categories = {category for case in cases for category in case["expected_categories"]}

    assert len(cases) >= 40
    assert len(benign) >= 12
    assert categories == {
        "authentication",
        "audit",
        "error",
        "network",
        "privilege",
        "service",
        "web",
    }


def test_representative_synthetic_corpus_is_exact_regression_gate() -> None:
    report = evaluate_detections.evaluate(DATASET, dataset_kind="synthetic")
    failures = evaluate_detections.regression_failures(
        report,
        min_precision=1.0,
        min_recall=1.0,
        min_case_accuracy=1.0,
        max_fp=0,
        max_fn=0,
    )

    assert report["cases"] >= 40
    assert report["precision"] == 1.0
    assert report["recall"] == 1.0
    assert report["case_exact_accuracy"] == 1.0
    assert report["fp"] == 0
    assert report["fn"] == 0
    assert failures == []
    assert "Synthetic regression evidence only" in report["limitations"]
