from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v211_historical_release_metadata_is_preserved() -> None:
    notes = _text("docs/RELEASE_V2.1.1.md")
    workflow = _text(".github/workflows/release-v2.1.1.yml")
    assert "# AegisLog v2.1.1" in notes
    assert "name: Release v2.1.1" in workflow
    assert 'RELEASE_TAG: v2.1.1' in workflow
    assert 'RELEASE_VERSION: 2.1.1' in workflow


def test_v211_release_notes_scope_patch_correctly() -> None:
    notes = _text("docs/RELEASE_V2.1.1.md")
    assert "Windows terminal UI polish patch" in notes
    assert "not Authenticode-signed" in notes
    assert "does not change detection" in notes
    assert "AI Analyst remains removed" in notes


def test_v211_workflow_remains_guarded_and_version_locked() -> None:
    workflow = _text(".github/workflows/release-v2.1.1.yml")
    assert 'RELEASE-v2.1.1' in workflow
    assert 'refs/heads/main' in workflow
    assert '--title "AegisLog v2.1.1"' in workflow
    assert 'docs/RELEASE_V2.1.1.md' in workflow
    assert '--latest' in workflow
    assert '2\\.1\\.1' in workflow


def test_v211_changelog_entry_precedes_v210() -> None:
    changelog = _text("CHANGELOG.md")
    v211 = changelog.index("## 2.1.1 - 2026-09-10")
    v210 = changelog.index("## 2.1.0 - 2026-09-10")
    assert v211 < v210
    assert re.search(r"## 2\.1\.1 .*?Mission Control", changelog, re.S)
