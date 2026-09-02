from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_live_file_prints_initial_snapshot_before_live_loop():
    text = (ROOT / "src" / "aegislog" / "commands_v13.py").read_text(encoding="utf-8")
    assert "console.print(render_realtime(state))" in text
    assert "Initial scan complete." in text
    assert text.index("console.print(render_realtime(state))") < text.index("with Live(")


def test_live_multi_prints_initial_snapshot_before_live_loop():
    text = (ROOT / "src" / "aegislog" / "commands_v14.py").read_text(encoding="utf-8")
    assert "console.print(render_multisource(state))" in text
    assert "Initial multi-source scan complete." in text
    assert text.index("console.print(render_multisource(state))") < text.index("with Live(")


def test_native_live_prints_initial_snapshot_before_live_loop():
    text = (ROOT / "src" / "aegislog" / "commands_v18.py").read_text(encoding="utf-8")
    assert "console.print(render_realtime(state))" in text
    assert "Initial native scan complete." in text
    assert text.index("console.print(render_realtime(state))") < text.index("with Live(")


def test_incident_explanation_uses_shared_semantic_theme():
    text = (ROOT / "src" / "aegislog" / "commands_v19.py").read_text(encoding="utf-8")
    assert "from .theme import" in text
    assert "border_style=INCIDENT" in text
    assert "border_style=WARNING" in text
    assert "border_style=SUCCESS" in text
    assert "title_style=f\"bold {ACCENT}\"" in text
    assert "severity_text(incident.severity)" in text
