from pathlib import Path
import re

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_v150_release_metadata_is_consistent():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    init_text = (ROOT / "src/aegislog/__init__.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/release-v1.5.0.yml").read_text(encoding="utf-8")
    notes = (ROOT / "docs/RELEASE_V1.5.0.md").read_text(encoding="utf-8")
    package_workflow = (ROOT / ".github/workflows/package.yml").read_text(encoding="utf-8")

    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)

    assert project["project"]["version"] == "1.5.0"
    assert match and match.group(1) == "1.5.0"
    assert "RELEASE_TAG: v1.5.0" in workflow
    assert "RELEASE_VERSION: 1.5.0" in workflow
    assert "RELEASE-v1.5.0" in workflow
    assert "AegisLog-v1.5.0-release-assets" in workflow
    assert "docs/RELEASE_V1.5.0.md" in workflow
    assert "aegislog_ai-1.5.0-py3-none-any.whl" in package_workflow
    assert "AegisLog-AI-v1.5.0-Customer-Bundle.zip" in package_workflow
    assert notes.startswith("# AegisLog AI v1.5.0")
