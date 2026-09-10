from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_TARGET = "31dbb523bd79959738b3a5e2a7ffc0ec6f5ceea2"
EXE_SHA256 = "61fc07de08a0597a350ed4438f838f29ae5ff616f58c86774d8bc059abcf2b1c"


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v211_is_current_published_stable() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")
    docs_index = _text("docs/README.md")

    assert "current published stable release is **v2.1.1**" in project_status
    assert "**Published stable:** v2.1.1" in project_status
    assert "currently released as **v2.1.1**" in roadmap
    assert "v2.1.1 — current stable release" in roadmap
    assert "[v2.1.1 release notes](RELEASE_V2.1.1.md)" in docs_index


def test_v211_release_target_and_checksum_are_recorded() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert RELEASE_TARGET in project_status
    assert RELEASE_TARGET in roadmap
    assert EXE_SHA256 in project_status
    assert "guarded v2.1.1 release workflow completed successfully" in project_status
    assert "Passed the guarded v2.1.1 release workflow" in roadmap


def test_v211_keeps_security_and_evidence_boundaries() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "unsigned" in project_status.lower()
    assert "synthetic regression evidence" in project_status.lower()
    assert "must not be fabricated as a release checkbox" in roadmap
    assert "AI Analyst" in project_status
