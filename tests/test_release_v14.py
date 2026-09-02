from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_historical_v140_release_workflow_is_removed():
    assert not (WORKFLOWS / "release-v1.4.0.yml").exists()


def test_v140_release_notes_remain_available_as_history():
    notes = (ROOT / "docs" / "RELEASE_V1.4.0.md").read_text(encoding="utf-8")
    assert notes.startswith("# AegisLog AI v1.4.0")
    assert "AegisLog.exe" in notes
    assert "No Python installation" in notes
    assert "read-only" in notes
    assert "4625" in notes
    assert "INC-XXXXXXXX" in notes


def test_historical_v142_release_workflow_is_removed():
    assert not (WORKFLOWS / "release-v1.4.2.yml").exists()


def test_v142_release_notes_remain_available_as_history():
    notes = (ROOT / "docs" / "RELEASE_V1.4.2.md").read_text(encoding="utf-8")
    assert notes.startswith("# AegisLog AI v1.4.2")
    assert "AegisLog.exe" in notes
    assert "read-only" in notes


def test_historical_v143_release_workflow_is_removed():
    assert not (WORKFLOWS / "release-v1.4.3.yml").exists()


def test_v143_release_notes_remain_available_as_history():
    notes = (ROOT / "docs" / "RELEASE_V1.4.3.md").read_text(encoding="utf-8")
    assert notes.startswith("# AegisLog AI v1.4.3")
    assert "AegisLog.exe" in notes
    assert "read-only" in notes


def test_historical_v144_release_workflow_is_removed():
    assert not (WORKFLOWS / "release-v1.4.4.yml").exists()


def test_v144_release_notes_remain_available_as_history():
    notes = (ROOT / "docs" / "RELEASE_V1.4.4.md").read_text(encoding="utf-8")
    assert notes.startswith("# AegisLog AI v1.4.4")
    assert "AegisLog.exe" in notes
    assert "read-only" in notes


def test_historical_v145_release_workflow_is_removed():
    assert not (WORKFLOWS / "release-v1.4.5.yml").exists()


def test_v145_release_notes_remain_available_as_history():
    notes = (ROOT / "docs" / "RELEASE_V1.4.5.md").read_text(encoding="utf-8")
    assert notes.startswith("# AegisLog AI v1.4.5")
    assert "AegisLog.exe" in notes
    assert "read-only" in notes


def test_v146_release_workflow_remains_available_as_history():
    workflow = (WORKFLOWS / "release-v1.4.6.yml").read_text(encoding="utf-8")
    assert "RELEASE-v1.4.6" in workflow
    assert "RELEASE_TAG: v1.4.6" in workflow
    assert "gh release create" in workflow
    assert "gh release upload" not in workflow


def test_current_v150_release_workflow_is_present():
    workflow = (WORKFLOWS / "release-v1.5.0.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "RELEASE-v1.5.0" in workflow
    assert "RELEASE_TAG: v1.5.0" in workflow
    assert "gh release create" in workflow
    assert "gh release upload" not in workflow
