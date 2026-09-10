from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.1.0"
TAG = "v2.1.0"


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v210_version_metadata_matches() -> None:
    project = tomllib.loads(_text("pyproject.toml"))
    init_text = _text("src/aegislog/__init__.py")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)

    assert project["project"]["version"] == VERSION
    assert match and match.group(1) == VERSION


def test_v210_package_paths_match_version() -> None:
    workflow = _text(".github/workflows/package.yml")
    assert "aegislog_ai-2.1.0-py3-none-any.whl" in workflow
    assert "AegisLog-AI-v2.1.0-Customer-Bundle.zip" in workflow
    assert "AegisLog-AI-v2.0.1-Customer-Bundle.zip" not in workflow


def test_v210_release_workflow_is_guarded_and_version_locked() -> None:
    workflow = _text(".github/workflows/release-v2.1.0.yml")

    assert "name: Release v2.1.0" in workflow
    assert 'RELEASE_TAG: v2.1.0' in workflow
    assert 'RELEASE_VERSION: 2.1.0' in workflow
    assert 'RELEASE-v2.1.0' in workflow
    assert 'refs/heads/main' in workflow
    assert 'python tools/release_preflight.py' in workflow
    assert 'Refuse to mutate an existing release or tag' in workflow
    assert 'Re-check immutability immediately before publication' in workflow
    assert 'AegisLog-v2.1.0-release-assets' in workflow
    assert '--title "AegisLog v2.1.0"' in workflow
    assert '--notes-file docs/RELEASE_V2.1.0.md' in workflow


def test_v210_release_workflow_gates_both_synthetic_corpora() -> None:
    workflow = _text(".github/workflows/release-v2.1.0.yml")
    common_gate = "--min-precision 1.0 --min-recall 1.0 --min-case-accuracy 1.0 --max-fp 0 --max-fn 0"

    assert "evaluation/labeled_events.jsonl --dataset-kind synthetic" in workflow
    assert "evaluation/representative_synthetic_v21.jsonl --dataset-kind synthetic" in workflow
    assert workflow.count(common_gate) == 2


def test_v210_release_notes_keep_claims_scoped() -> None:
    notes = _text("docs/RELEASE_V2.1.0.md")
    assert "AegisLog v2.1.0" in notes
    assert "synthetic regression fixtures" in notes
    assert "not evidence of deployment-specific or general real-world detection effectiveness" in notes
    assert "not Authenticode-signed" in notes
    assert "AI Analyst" in notes
