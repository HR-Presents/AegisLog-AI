from pathlib import Path


def test_v141_release_artifacts_remain_consistent():
    workflow = Path(".github/workflows/release-v1.4.1.yml").read_text(encoding="utf-8")
    notes = Path("docs/RELEASE_V1.4.1.md").read_text(encoding="utf-8")

    assert "RELEASE_TAG: v1.4.1" in workflow
    assert "RELEASE_VERSION: 1.4.1" in workflow
    assert "RELEASE-v1.4.1" in workflow
    assert "AegisLog-v1.4.1-release-assets" in workflow
    assert "docs/RELEASE_V1.4.1.md" in workflow
    assert notes.startswith("# AegisLog AI v1.4.1")
