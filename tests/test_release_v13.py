from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_historical_v13_release_workflows_are_removed():
    assert not (WORKFLOWS / "release-v1.3.0.yml").exists()
    assert not (WORKFLOWS / "release-v1.3.1.yml").exists()


def test_v131_release_notes_remain_available_as_history():
    notes = (ROOT / "docs" / "RELEASE_V1.3.1.md").read_text(encoding="utf-8")
    assert notes.startswith("# AegisLog AI v1.3.1")
    assert "AegisLog.exe" in notes
    assert "No Python installation" in notes
    assert "AegisLog.exe.sha256" in notes
