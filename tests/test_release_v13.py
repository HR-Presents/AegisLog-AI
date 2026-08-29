from pathlib import Path
import re

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_v131_version_metadata_matches():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    init_text = (ROOT / "src" / "aegislog" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
    assert project["project"]["version"] == "1.3.1"
    assert match and match.group(1) == "1.3.1"


def test_v131_release_workflow_is_manual_and_immutable():
    workflow = (ROOT / ".github" / "workflows" / "release-v1.3.1.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "RELEASE-v1.3.1" in workflow
    assert 'RELEASE_TAG: v1.3.1' in workflow
    assert 'refs/heads/main' in workflow
    assert 'gh release view "$RELEASE_TAG"' in workflow
    assert 'git ls-remote --exit-code --tags origin "refs/tags/$RELEASE_TAG"' in workflow
    assert "gh release create" in workflow
    assert "gh release upload" not in workflow


def test_v131_release_publishes_only_customer_exe_and_checksum():
    workflow = (ROOT / ".github" / "workflows" / "release-v1.3.1.yml").read_text(encoding="utf-8")
    assert "release-assets/AegisLog.exe" in workflow
    assert "release-assets/AegisLog.exe.sha256" in workflow
    assert "AegisLog-AI-v1.3.1-Customer-Bundle.zip" not in workflow


def test_v131_release_artifact_is_staged_flat_for_linux_checksum_verification():
    workflow = (ROOT / ".github" / "workflows" / "release-v1.3.1.yml").read_text(encoding="utf-8")
    assert 'Copy-Item "dist\\AegisLog.exe" "release-assets\\AegisLog.exe"' in workflow
    assert '"release-assets\\AegisLog.exe.sha256"' in workflow
    assert "path: release-assets/*" in workflow
    assert "test -f AegisLog.exe" in workflow
    assert "test -f AegisLog.exe.sha256" in workflow
    assert "sha256sum --check AegisLog.exe.sha256" in workflow


def test_v131_release_notes_describe_friendly_single_file_delivery():
    notes = (ROOT / "docs" / "RELEASE_V1.3.1.md").read_text(encoding="utf-8")
    assert "AegisLog.exe" in notes
    assert "No Python installation" in notes
    assert "AegisLog.exe.sha256" in notes
    assert "Command Mode" in notes
    assert "numbered shortcuts" in notes


def test_previous_v130_release_workflow_remains_present_and_unchanged_in_purpose():
    workflow = (ROOT / ".github" / "workflows" / "release-v1.3.0.yml").read_text(encoding="utf-8")
    assert "RELEASE-v1.3.0" in workflow
    assert 'RELEASE_TAG: v1.3.0' in workflow
    assert "gh release upload" not in workflow
