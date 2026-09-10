from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v213_version_metadata_is_consistent() -> None:
    assert 'version = "2.1.3"' in _text("pyproject.toml")
    assert '__version__ = "2.1.3"' in _text("src/aegislog/__init__.py")


def test_v213_release_notes_preserve_security_boundaries() -> None:
    notes = _text("docs/RELEASE_V2.1.3.md")
    assert "front-facing Falcon identity" in notes
    assert "not Authenticode-signed" in notes
    assert "does not change detection rules" in notes
    assert "No mock security results" in notes
    assert "AI Analyst remains removed" in notes
    assert "Synthetic evaluation remains regression evidence only" in notes


def test_v213_workflow_is_guarded_version_locked_and_smokes_approved_ui() -> None:
    workflow = _text(".github/workflows/release-v2.1.3.yml")
    assert "name: Release v2.1.3" in workflow
    assert "RELEASE_TAG: v2.1.3" in workflow
    assert "RELEASE_VERSION: 2.1.3" in workflow
    assert "RELEASE-v2.1.3" in workflow
    assert "refs/heads/main" in workflow
    assert '--title "AegisLog v2.1.3"' in workflow
    assert "docs/RELEASE_V2.1.3.md" in workflow
    assert "--latest" in workflow
    assert "2\\.1\\.3" in workflow
    assert "MISSION CONTROL" in workflow
    assert "ANALYZE LOG" in workflow
    assert "LIVE MONITOR" in workflow
    assert "HEALTH" in workflow
    assert "TOP FINDINGS" in workflow
    assert "ANALYST FOCUS" in workflow
    assert "Analysis complete" in workflow
    assert "RAW EVIDENCE" in workflow
    assert "INVESTIGATION TIMELINE" in workflow
    assert "STAY AHEAD" in workflow


def test_package_workflow_uses_v213_artifact_names() -> None:
    package = _text(".github/workflows/package.yml")
    assert "aegislog_ai-2.1.3-py3-none-any.whl" in package
    assert "AegisLog-AI-v2.1.3-Customer-Bundle.zip" in package
    assert "AegisLog-AI-v2.1.2-Customer-Bundle.zip" not in package
