from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v146_release_artifacts_remain_available_as_history():
    workflow = (ROOT / ".github/workflows/release-v1.4.6.yml").read_text(encoding="utf-8")
    notes = (ROOT / "docs/RELEASE_V1.4.6.md").read_text(encoding="utf-8")

    assert "RELEASE_TAG: v1.4.6" in workflow
    assert "RELEASE_VERSION: 1.4.6" in workflow
    assert "RELEASE-v1.4.6" in workflow
    assert "AegisLog-v1.4.6-release-assets" in workflow
    assert "docs/RELEASE_V1.4.6.md" in workflow
    assert notes.startswith("# AegisLog AI v1.4.6")
