from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_public_cli_branding_uses_aegislog_name() -> None:
    cli = _text("src/aegislog/cli.py")
    assert "AegisLog AI" not in cli
    assert "AEGISLOG AI" not in cli
    assert 'AegisLog {__version__}' in cli


def test_customer_bundle_has_no_stale_ai_branding() -> None:
    paths = [
        "customer_bundle/INSTALL_WINDOWS.bat",
        "customer_bundle/INSTALL_LINUX_MACOS.sh",
        "customer_bundle/OPEN_AEGISLOG_TERMINAL.bat",
        "customer_bundle/OPEN_AEGISLOG_TERMINAL.sh",
        "customer_bundle/START_AEGISLOG.bat",
        "customer_bundle/START_AEGISLOG.sh",
        "customer_bundle/README.txt",
    ]
    for path in paths:
        text = _text(path)
        assert "AegisLog AI" not in text, path
        assert "AEGISLOG AI" not in text, path


def test_readme_matches_v200_mission_control() -> None:
    readme = _text("README.md")
    assert "v2.0.0" in readme
    assert "VERSION 1.7" not in readme
    assert "SELECT  ›" not in readme
    assert "01-09 select" in readme
    assert "real `aegis@console >` shell prompt" in readme


def test_current_docs_identify_v200_as_stable() -> None:
    docs_index = _text("docs/README.md")
    project_status = _text("docs/PROJECT_STATUS.md")
    roadmap = _text("docs/ROADMAP.md")

    assert "Published stable:** [v2.0.0" in docs_index
    assert "current published stable release is **v2.0.0**" in project_status
    assert "currently released as **v2.0.0**" in roadmap
    assert "current published stable release is **v1.6.0**" not in project_status
    assert "currently released as **v1.6.0**" not in roadmap
