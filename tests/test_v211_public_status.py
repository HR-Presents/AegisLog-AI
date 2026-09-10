from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_TARGET = "c01247b34a2dd54c863dd142c618f03e184af8f8"
EXE_SHA256 = "1ddda99e03fd36ba1816b1567a28b8cc23d410583f34771c1287f9e3c1a28155"


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v213_is_current_published_stable() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")
    docs_index = _text("docs/README.md")

    assert "current published stable release is **v2.1.3**" in project_status
    assert "**Published stable:** v2.1.3" in project_status
    assert "currently released as **v2.1.3**" in roadmap
    assert "v2.1.3 — current stable release" in roadmap
    assert "[v2.1.3 release notes](RELEASE_V2.1.3.md)" in docs_index


def test_v213_release_target_and_checksum_are_recorded() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")

    assert RELEASE_TARGET in project_status
    assert EXE_SHA256 in project_status
    assert "v2.1.3" in project_status
    assert "AegisLog.exe.sha256" in project_status


def test_v213_keeps_security_and_evidence_boundaries() -> None:
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "unsigned" in project_status.lower()
    assert "synthetic regression evidence" in project_status.lower()
    assert "real-world" in roadmap.lower()
    assert "AI Analyst" in project_status
