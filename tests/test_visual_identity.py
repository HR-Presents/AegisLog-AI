from __future__ import annotations

from pathlib import Path

from rich.console import Console

from aegislog import commands_v145
from aegislog.theme import ACCENT, MUTED, NEUTRAL


ROOT = Path(__file__).resolve().parents[1]


def _render(renderable, width: int = 100) -> str:
    console = Console(width=width, record=True, force_terminal=False, color_system=None)
    console.print(renderable)
    return console.export_text()


def test_home_has_prominent_brand_and_feature_hierarchy() -> None:
    text = _render(commands_v145._home(100))
    assert "A E G I S L O G" in text
    assert "DEFENSIVE LOG INVESTIGATION" in text
    assert "INVESTIGATION" in text
    assert "ANALYZE" in text
    assert "MONITORING" in text
    assert "LIVE MONITOR" in text
    assert "SYSTEM READY" in text
    assert "AI ANALYST" not in text.upper()
    assert "OLLAMA" not in text.upper()
    assert "OPENAI" not in text.upper()


def test_workspace_keeps_compact_brand_signature() -> None:
    text = _render(commands_v145._operation_header("Analyze", "Investigate retained evidence", screen_width=100))
    assert "AEGISLOG" in text
    assert "ANALYZE" in text
    assert "Investigate retained evidence" in text
    assert "LOCAL / READ-ONLY" in text


def test_palette_uses_controlled_blue_identity() -> None:
    assert ACCENT == "#4C8DFF"
    assert NEUTRAL == "#E7EDF6"
    assert MUTED == "#718096"


def test_readme_uses_brand_asset_and_strong_capabilities() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert 'docs/assets/aegislog-logo.svg' in readme
    assert "Core capabilities" in readme
    assert "**ANALYZE**" in readme
    assert "**LIVE MONITOR**" in readme
    assert "**INCIDENTS**" in readme


def test_logo_uses_professional_midnight_blue_system() -> None:
    logo = (ROOT / "docs" / "assets" / "aegislog-logo.svg").read_text(encoding="utf-8")
    assert "#080D14" in logo
    assert "#4C8DFF" in logo
    assert "DEFENSIVE LOG INVESTIGATION" in logo
    assert "LOCAL-FIRST" in logo
