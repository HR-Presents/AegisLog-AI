from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v212_historical_release_notes_preserve_security_boundaries() -> None:
    notes = _text("docs/RELEASE_V2.1.2.md")
    assert "terminal-first security command-center" in notes
    assert "not Authenticode-signed" in notes
    assert "does not change detection rules" in notes
    assert "No mock security results" in notes
    assert "AI Analyst remains removed" in notes
    assert "Synthetic evaluation remains regression evidence only" in notes


def test_v212_historical_workflow_remains_version_locked() -> None:
    workflow = _text(".github/workflows/release-v2.1.2.yml")
    assert "name: Release v2.1.2" in workflow
    assert 'RELEASE_TAG: v2.1.2' in workflow
    assert 'RELEASE_VERSION: 2.1.2' in workflow
    assert 'RELEASE-v2.1.2' in workflow
    assert '--title "AegisLog v2.1.2"' in workflow
    assert 'docs/RELEASE_V2.1.2.md' in workflow
