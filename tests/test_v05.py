from pathlib import Path

from aegislog.hunt import extract_indicators
from aegislog.plugins import apply_rules, load_rules


def test_rule_plugin_load_and_apply(tmp_path: Path):
    plugin = tmp_path / "custom.py"
    plugin.write_text("RULES = [{'id':'demo','severity':'HIGH','category':'custom','title':'Custom signal','pattern':'danger-event','recommendation':'Review surrounding telemetry.'}]\n", encoding="utf-8")
    rules, errors = load_rules(tmp_path)
    assert not errors
    findings = apply_rules(["danger-event from service"], rules)
    assert findings[0].title == "Custom signal"


def test_invalid_rule_plugin_isolated(tmp_path: Path):
    (tmp_path / "bad.py").write_text("RULES = [{'id':'bad'}]\n", encoding="utf-8")
    rules, errors = load_rules(tmp_path)
    assert not rules
    assert errors


def test_indicator_extraction_is_bounded_and_defensive():
    indicators = extract_indicators("failed from 203.0.113.10 host.example.org then 203.0.113.10")
    assert indicators["ipv4"] == ["203.0.113.10"]
    assert indicators["domains"] == ["host.example.org"]
