from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v21_development_is_recorded_without_claiming_release() -> None:
    changelog = _text("CHANGELOG.md")
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "### v2.1 development" in changelog
    assert "No unreleased changes yet." not in changelog
    assert "v2.1 development line is active" in project_status
    assert "v2.1 development line is active" in roadmap
    assert "not yet a published release" in project_status
    assert "v2.1.0 has not yet been published" in roadmap


def test_current_published_stable_remains_v201_until_release() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "current published stable release is **v2.0.1**" in project_status
    assert "currently released as **v2.0.1**" in roadmap
    assert "Published stable:** v2.1.0" not in project_status
    assert "currently released as **v2.1.0**" not in roadmap


def test_v21_docs_keep_evidence_claims_scoped() -> None:
    changelog = _text("CHANGELOG.md")
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    for text in (changelog, project_status, roadmap):
        assert "synthetic" in text.lower()
        assert "real-world" in text.lower()

    assert "must not be represented as deployment-specific" in project_status
    assert "must not be fabricated as a release checkbox" in roadmap


def test_v21_release_gate_names_all_required_checks() -> None:
    roadmap = _text("docs/ROADMAP.md")
    required = (
        "CI",
        "Security checks",
        "Package build",
        "Windows single executable",
        "Runtime lock audit",
        "Validation toolchain lock audit",
        "Build toolchain lock audit",
    )
    for check in required:
        assert check in roadmap
