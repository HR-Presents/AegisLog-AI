from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.1.0"
TAG = "v2.1.0"


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v210_historical_release_workflow_is_version_locked() -> None:
    workflow = _text(".github/workflows/release-v2.1.0.yml")

    assert "name: Release v2.1.0" in workflow
    assert f"RELEASE_TAG: {TAG}" in workflow
    assert f"RELEASE_VERSION: {VERSION}" in workflow
    assert "RELEASE-v2.1.0" in workflow
    assert "refs/heads/main" in workflow
    assert "python tools/release_preflight.py" in workflow
    assert "Refuse to mutate an existing release or tag" in workflow
    assert "Re-check immutability immediately before publication" in workflow
    assert "AegisLog-v2.1.0-release-assets" in workflow
    assert '--title "AegisLog v2.1.0"' in workflow
    assert "--notes-file docs/RELEASE_V2.1.0.md" in workflow


def test_v210_historical_release_workflow_gates_both_synthetic_corpora() -> None:
    workflow = _text(".github/workflows/release-v2.1.0.yml")
    common_gate = "--min-precision 1.0 --min-recall 1.0 --min-case-accuracy 1.0 --max-fp 0 --max-fn 0"

    assert "evaluation/labeled_events.jsonl --dataset-kind synthetic" in workflow
    assert "evaluation/representative_synthetic_v21.jsonl --dataset-kind synthetic" in workflow
    assert workflow.count(common_gate) == 2


def test_v210_historical_release_notes_keep_claims_scoped() -> None:
    notes = _text("docs/RELEASE_V2.1.0.md")
    assert "AegisLog v2.1.0" in notes
    assert "synthetic regression fixtures" in notes
    assert "not evidence of deployment-specific or general real-world detection effectiveness" in notes
    assert "not Authenticode-signed" in notes
    assert "AI Analyst" in notes
