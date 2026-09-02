from pathlib import Path
import re

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


def test_v145_release_metadata_is_consistent():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    init_text = Path("src/aegislog/__init__.py").read_text(encoding="utf-8")
    workflow = Path(".github/workflows/release-v1.4.5.yml").read_text(encoding="utf-8")
    notes = Path("docs/RELEASE_V1.4.5.md").read_text(encoding="utf-8")
    package_workflow = Path(".github/workflows/package.yml").read_text(encoding="utf-8")

    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)

    assert project["project"]["version"] == "1.4.5"
    assert match and match.group(1) == "1.4.5"
    assert "RELEASE_TAG: v1.4.5" in workflow
    assert "RELEASE_VERSION: 1.4.5" in workflow
    assert "RELEASE-v1.4.5" in workflow
    assert "AegisLog-v1.4.5-release-assets" in workflow
    assert "docs/RELEASE_V1.4.5.md" in workflow
    assert "aegislog_ai-1.4.5-py3-none-any.whl" in package_workflow
    assert "AegisLog-AI-v1.4.5-Customer-Bundle.zip" in package_workflow
    assert notes.startswith("# AegisLog AI v1.4.5")
