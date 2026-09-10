from pathlib import Path
import re

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_v180_release_metadata_is_consistent():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    init_text = (ROOT / "src/aegislog/__init__.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/release-v1.8.0.yml").read_text(encoding="utf-8")
    historical_workflow = (ROOT / ".github/workflows/release-v1.7.0.yml").read_text(encoding="utf-8")
    older_workflow = (ROOT / ".github/workflows/release-v1.6.3.yml").read_text(encoding="utf-8")
    older_notes_workflow = (ROOT / ".github/workflows/release-v1.6.2.yml").read_text(encoding="utf-8")
    retired_workflow = (ROOT / ".github/workflows/release-v1.6.0.yml").read_text(encoding="utf-8")
    notes = (ROOT / "docs/RELEASE_V1.8.0.md").read_text(encoding="utf-8")
    historical_notes = (ROOT / "docs/RELEASE_V1.7.0.md").read_text(encoding="utf-8")
    older_notes = (ROOT / "docs/RELEASE_V1.6.3.md").read_text(encoding="utf-8")
    older_release_notes = (ROOT / "docs/RELEASE_V1.6.2.md").read_text(encoding="utf-8")
    retired_notes = (ROOT / "docs/RELEASE_V1.6.0.md").read_text(encoding="utf-8")
    package_workflow = (ROOT / ".github/workflows/package.yml").read_text(encoding="utf-8")

    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)

    assert project["project"]["version"] == "1.8.0"
    assert match and match.group(1) == "1.8.0"
    assert "RELEASE_TAG: v1.8.0" in workflow
    assert "RELEASE_VERSION: 1.8.0" in workflow
    assert "RELEASE-v1.8.0" in workflow
    assert "AegisLog-v1.8.0-release-assets" in workflow
    assert "docs/RELEASE_V1.8.0.md" in workflow
    assert "Mission Control banner did not report v1.8.0" in workflow
    assert "Removed AI surface reappeared in public help" in workflow
    assert "Removed AI surface reappeared in Mission Control" in workflow
    assert "aegislog_ai-1.8.0-py3-none-any.whl" in package_workflow
    assert "AegisLog-AI-v1.8.0-Customer-Bundle.zip" in package_workflow
    assert notes.startswith("# AegisLog v1.8.0")

    assert "RELEASE_TAG: v1.7.0" in historical_workflow
    assert historical_notes.startswith("# AegisLog v1.7.0")
    assert "RELEASE_TAG: v1.6.3" in older_workflow
    assert older_notes.startswith("# AegisLog AI v1.6.3")
    assert "RELEASE_TAG: v1.6.2" in older_notes_workflow
    assert older_release_notes.startswith("# AegisLog AI v1.6.2")
    assert "Release v1.6.0 (retired)" in retired_workflow
    assert "v1.6.0 was already published on 2026-09-02" in retired_workflow
    assert "exit 1" in retired_workflow
    assert retired_notes.startswith("# AegisLog AI v1.6.0")
    assert "currently unsigned" in retired_notes
