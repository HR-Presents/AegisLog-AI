from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v210_release_remains_recorded_historically() -> None:
    changelog = _text("CHANGELOG.md")
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "## 2.1.0 - 2026-09-10" in changelog
    assert "v2.1.0" in project_status
    assert "v2.1.0" in roadmap


def test_v21_docs_no_longer_claim_release_is_pending() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "not yet a published release" not in project_status
    assert "has not yet been published" not in roadmap
    assert "v2.1.3" in project_status
    assert "v2.1.3" in roadmap


def test_v21_docs_keep_evidence_claims_scoped() -> None:
    changelog = _text("CHANGELOG.md")
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    for text in (changelog, project_status, roadmap):
        assert "synthetic" in text.lower()
        assert "real-world" in text.lower()

    assert "synthetic regression evidence" in project_status.lower()
    assert "independently validated" in roadmap.lower()


def test_v210_docs_preserve_historical_release_verification() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "v2.1.0" in project_status
    assert "AegisLog.exe.sha256" in project_status
    assert "v2.1.0" in roadmap
    assert "checksum" in roadmap.lower()
