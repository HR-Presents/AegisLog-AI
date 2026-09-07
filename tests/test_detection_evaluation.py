import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evaluation" / "labeled_events.jsonl"
MODULE_PATH = ROOT / "tools" / "evaluate_detections.py"
SPEC = importlib.util.spec_from_file_location("aegislog_detection_evaluator", MODULE_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - importlib platform guard
    raise RuntimeError("could not load detection evaluator module")
EVALUATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATOR)


evaluate = EVALUATOR.evaluate
regression_failures = EVALUATOR.regression_failures
_wilson_interval = EVALUATOR._wilson_interval


def test_synthetic_report_includes_confidence_intervals_and_exact_accuracy():
    report = evaluate(FIXTURE, dataset_kind="synthetic")

    assert report["cases"] == 12
    assert report["precision"] == 1.0
    assert report["recall"] == 1.0
    assert report["case_exact_accuracy"] == 1.0
    assert report["precision_ci95"]["lower"] < 1.0
    assert report["precision_ci95"]["upper"] == 1.0
    assert report["recall_ci95"]["lower"] < 1.0
    assert "Synthetic regression evidence only" in report["limitations"]


def test_wilson_interval_is_bounded_and_non_degenerate_for_small_perfect_sample():
    interval = _wilson_interval(8, 8)

    assert 0.0 < interval["lower"] < 1.0
    assert interval["upper"] == 1.0
    assert interval["successes"] == 8
    assert interval["total"] == 8


def test_external_dataset_requires_provenance():
    with pytest.raises(ValueError, match="external datasets require"):
        evaluate(FIXTURE, dataset_kind="external")


def test_external_dataset_records_provenance():
    report = evaluate(
        FIXTURE,
        dataset_kind="external",
        provenance="Sanitized independently labeled test corpus; sampling documented separately.",
    )

    assert report["dataset_kind"] == "external"
    assert report["provenance"].startswith("Sanitized independently labeled")
    assert "sampling uncertainty" in report["limitations"]


def test_regression_gate_reports_each_failed_threshold():
    report = {
        "precision": 0.8,
        "recall": 0.75,
        "case_exact_accuracy": 0.7,
        "fp": 3,
        "fn": 2,
    }

    failures = regression_failures(
        report,
        min_precision=0.9,
        min_recall=0.9,
        min_case_accuracy=0.8,
        max_fp=1,
        max_fn=1,
    )

    assert len(failures) == 5
    assert any("precision" in failure for failure in failures)
    assert any("false positives" in failure for failure in failures)


def test_duplicate_case_ids_are_rejected(tmp_path: Path):
    dataset = tmp_path / "duplicate.jsonl"
    row = '{"id":"same","expected_categories":[],"lines":["ok"]}\n'
    dataset.write_text(row + row, encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate evaluation case id"):
        evaluate(dataset)
