from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v150_release_artifacts_remain_as_historical_records():
    workflow = (ROOT / ".github/workflows/release-v1.5.0.yml").read_text(encoding="utf-8")
    notes = (ROOT / "docs/RELEASE_V1.5.0.md").read_text(encoding="utf-8")

    assert "RELEASE_TAG: v1.5.0" in workflow
    assert "RELEASE-v1.5.0" in workflow
    assert "AegisLog-v1.5.0-release-assets" in workflow
    assert "docs/RELEASE_V1.5.0.md" in workflow
    assert notes.startswith("# AegisLog AI v1.5.0")
