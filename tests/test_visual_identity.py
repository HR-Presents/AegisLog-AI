from __future__ import annotations

from pathlib import Path

from rich.console import Console

from aegislog import commands_v145
from aegislog.theme import ACCENT, BLUE, CYAN, LIME, MAGENTA, MUTED, NEUTRAL, ORANGE, VIOLET

ROOT = Path(__file__).resolve().parents[1]


def _render(renderable, width: int = 100) -> str:
    console = Console(width=width, record=True, force_terminal=False, color_system=None)
    console.print(renderable)
    return console.export_text()


def test_home_has_prominent_brand_and_feature_hierarchy() -> None:
    text = _render(commands_v145._home(100))
    assert "DEFENSIVE LOG INVESTIGATION" in text
    assert "MADE BY HR-PRESENTS" in text
    assert "INVESTIGATE" in text
    assert "MONITOR & INVESTIGATE" in text
    assert "UTILITIES" in text
    assert "ANALYZE LOG" in text
    assert "LIVE MONITOR" in text
    assert "SYSTEM READY" in text
    assert "AI ANALYST" not in text.upper()
    assert "VERSION" not in text.upper()
    assert "<F>" not in text


def test_workspace_keeps_compact_brand_signature() -> None:
    text = _render(commands_v145._operation_header("Analyze", "Investigate retained evidence", screen_width=100))
    assert "AEGISLOG" in text
    assert "ANALYZE" in text
    assert "Investigate retained evidence" in text
    assert "LOCAL / READ-ONLY" in text
    assert "MADE BY HR-PRESENTS" in text


def test_palette_uses_high_contrast_multicolor_identity() -> None:
    assert ACCENT == "#22D3EE"
    assert NEUTRAL == "#F8FAFC"
    assert MUTED == "#94A3B8"
    assert len({ACCENT, BLUE, CYAN, LIME, MAGENTA, ORANGE, VIOLET}) == 7
    assert set(commands_v145._MENU_TONES.values()) <= {ACCENT, BLUE, CYAN, "#67E8F9"}


def test_readme_uses_strong_capabilities_and_product_identity() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "# AEGISLOG" in readme or "docs/assets/aegislog-logo.svg" in readme
    assert "Core capabilities" in readme
    assert "**ANALYZE**" in readme
    assert "**LIVE MONITOR**" in readme
    assert "**INCIDENTS**" in readme
    assert "LOCAL-FIRST" in readme
    assert "READ-ONLY" in readme
    assert "DETERMINISTIC" in readme


def test_logo_asset_keeps_professional_midnight_blue_system() -> None:
    logo = (ROOT / "docs" / "assets" / "aegislog-logo.svg").read_text(encoding="utf-8")
    assert "#080D14" in logo
    assert "#4C8DFF" in logo
    assert "DEFENSIVE LOG INVESTIGATION" in logo
    assert "LOCAL-FIRST" in logo
