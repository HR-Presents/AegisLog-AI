from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_TARGET = "9eefb18af494d2488f0795eb7326470f642058f2"


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v21_release_is_recorded_as_published_stable() -> None:
    changelog = _text("CHANGELOG.md")
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "## 2.1.0 - 2026-09-10" in changelog
    assert "current published stable release is **v2.1.0**" in project_status
    assert "Published stable:** v2.1.0" in project_status
    assert "currently released as **v2.1.0**" in roadmap
    assert "v2.1.0 — current stable release" in roadmap
    assert RELEASE_TARGET in project_status
    assert RELEASE_TARGET in roadmap


def test_v21_docs_no_longer_claim_release_is_pending() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "not yet a published release" not in project_status
    assert "v2.1.0 has not yet been published" not in roadmap
    assert "current published stable release is **v2.0.1**" not in project_status
    assert "currently released as **v2.0.1**" not in roadmap


def test_v21_docs_keep_evidence_claims_scoped() -> None:
    changelog = _text("CHANGELOG.md")
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    for text in (changelog, project_status, roadmap):
        assert "synthetic" in text.lower()
        assert "real-world" in text.lower()

    assert "must not be represented as deployment-specific" in project_status
    assert "must not be fabricated as a release checkbox" in roadmap


def test_v21_docs_record_release_verification_and_artifacts() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "guarded v2.1.0 release workflow completed successfully" in project_status
    assert "AegisLog.exe.sha256" in project_status
    assert "Passed the required exact-head CI" in roadmap
    assert "Passed the guarded v2.1.0 release workflow" in roadmap
    assert "matching SHA-256 checksum" in roadmap
