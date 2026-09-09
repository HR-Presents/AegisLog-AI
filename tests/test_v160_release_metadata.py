from pathlib import Path
import re

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_v163_release_metadata_is_consistent():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    init_text = (ROOT / "src/aegislog/__init__.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/release-v1.6.3.yml").read_text(encoding="utf-8")
    historical_workflow = (ROOT / ".github/workflows/release-v1.6.2.yml").read_text(encoding="utf-8")
    retired_workflow = (ROOT / ".github/workflows/release-v1.6.0.yml").read_text(encoding="utf-8")
    notes = (ROOT / "docs/RELEASE_V1.6.3.md").read_text(encoding="utf-8")
    historical_notes = (ROOT / "docs/RELEASE_V1.6.2.md").read_text(encoding="utf-8")
    retired_notes = (ROOT / "docs/RELEASE_V1.6.0.md").read_text(encoding="utf-8")
    package_workflow = (ROOT / ".github/workflows/package.yml").read_text(encoding="utf-8")

    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)

    assert project["project"]["version"] == "1.6.3"
    assert match and match.group(1) == "1.6.3"
    assert "RELEASE_TAG: v1.6.3" in workflow
    assert "RELEASE_VERSION: 1.6.3" in workflow
    assert "RELEASE-v1.6.3" in workflow
    assert "AegisLog-v1.6.3-release-assets" in workflow
    assert "docs/RELEASE_V1.6.3.md" in workflow
    assert "Mission Control banner did not report v1.6.3" in workflow
    assert "aegislog_ai-1.6.3-py3-none-any.whl" in package_workflow
    assert "AegisLog-AI-v1.6.3-Customer-Bundle.zip" in package_workflow
    assert notes.startswith("# AegisLog AI v1.6.3")

    assert "RELEASE_TAG: v1.6.2" in historical_workflow
    assert historical_notes.startswith("# AegisLog AI v1.6.2")
    assert "Release v1.6.0 (retired)" in retired_workflow
    assert "v1.6.0 was already published on 2026-09-02" in retired_workflow
    assert "exit 1" in retired_workflow
    assert retired_notes.startswith("# AegisLog AI v1.6.0")
    assert "currently unsigned" in retired_notes
