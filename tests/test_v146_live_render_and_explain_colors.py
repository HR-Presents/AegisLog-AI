from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_live_file_opens_single_dashboard_workspace():
    text = (ROOT / "src" / "aegislog" / "commands_v13.py").read_text(encoding="utf-8")
    assert "console.print(render_realtime(state))" not in text
    assert "Initial scan complete. Opening live workspace." in text
    assert '"auto_refresh": False' in text
    assert '"screen": True' in text


def test_live_multi_opens_single_dashboard_workspace():
    text = (ROOT / "src" / "aegislog" / "commands_v14.py").read_text(encoding="utf-8")
    assert "console.print(render_multisource(state))" not in text
    assert "Initial multi-source scan complete. Opening live workspace." in text
    assert '"auto_refresh": False' in text
    assert '"screen": True' in text


def test_native_live_opens_single_dashboard_workspace():
    text = (ROOT / "src" / "aegislog" / "commands_v18.py").read_text(encoding="utf-8")
    assert "console.print(render_realtime(state))" not in text
    assert "Initial native scan complete. Opening live workspace." in text
    assert '"auto_refresh": False' in text
    assert '"screen": True' in text


def test_incident_explanation_uses_shared_semantic_theme():
    text = (ROOT / "src" / "aegislog" / "commands_v19.py").read_text(encoding="utf-8")
    assert "from .theme import" in text
    assert "border_style=INCIDENT" in text
    assert "border_style=WARNING" in text
    assert "border_style=SUCCESS" in text
    assert "title_style=f\"bold {ACCENT}\"" in text
    assert "severity_text(incident.severity)" in text
