from pathlib import Path


def test_v141_release_notes_remain_and_historical_workflow_is_removed():
    workflow = Path(".github/workflows/release-v1.4.1.yml")
    notes = Path("docs/RELEASE_V1.4.1.md").read_text(encoding="utf-8")

    assert not workflow.exists()
    assert notes.startswith("# AegisLog AI v1.4.1")
    assert "AegisLog.exe" in notes
