from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v140_release_metadata_is_preserved_in_historical_workflow():
    workflow = (ROOT / ".github" / "workflows" / "release-v1.4.0.yml").read_text(encoding="utf-8")
    assert "RELEASE_TAG: v1.4.0" in workflow
    assert "RELEASE_VERSION: 1.4.0" in workflow
    assert '== "1.4.0"' in workflow


def test_v140_release_workflow_is_manual_and_refuses_mutation():
    workflow = (ROOT / ".github" / "workflows" / "release-v1.4.0.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "RELEASE-v1.4.0" in workflow
    assert "RELEASE_TAG: v1.4.0" in workflow
    assert "refs/heads/main" in workflow
    assert 'gh release view "$RELEASE_TAG"' in workflow
    assert 'git ls-remote --exit-code --tags origin "refs/tags/$RELEASE_TAG"' in workflow
    assert "gh release create" in workflow
    assert "gh release upload" not in workflow


def test_v140_release_runs_full_quality_gates_and_exe_smoke_tests():
    workflow = (ROOT / ".github" / "workflows" / "release-v1.4.0.yml").read_text(encoding="utf-8")
    for expected in (
        "ruff check .",
        "pytest -q",
        "bandit -q -r src",
        "pip-audit",
        "python -m build",
        "python -m twine check dist/*",
        "AegisLog.exe --version",
        "AegisLog.exe doctor",
        "AegisLog.exe native-sources",
        "AegisLog.exe incidents --help",
        "AegisLog.exe investigate --help",
        "AegisLog.exe explain --help",
    ):
        assert expected in workflow


def test_v140_release_publishes_only_exe_and_checksum():
    workflow = (ROOT / ".github" / "workflows" / "release-v1.4.0.yml").read_text(encoding="utf-8")
    assert "release-assets/AegisLog.exe" in workflow
    assert "release-assets/AegisLog.exe.sha256" in workflow
    assert "path: release-assets/*" in workflow
    assert "sha256sum --check AegisLog.exe.sha256" in workflow
    assert "AegisLog-v1.4.0-release-assets" in workflow


def test_v140_release_notes_cover_customer_and_safety_model():
    notes = (ROOT / "docs" / "RELEASE_V1.4.0.md").read_text(encoding="utf-8")
    assert "AegisLog.exe" in notes
    assert "No Python installation" in notes
    assert "read-only" in notes
    assert "not digitally signed" in notes
    assert "4625" in notes
    assert "INC-XXXXXXXX" in notes
