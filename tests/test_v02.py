from aegislog.ai import InvestigationContext, build_safe_prompt
from aegislog.anomaly import score_events
from aegislog.engine import Finding
from aegislog.parsers import parse_line


def test_nginx_parser():
    event = parse_line('203.0.113.8 - - [29/Aug/2026:12:00:00 +0000] "GET /admin HTTP/1.1" 404 12')
    assert event.source == "web"
    assert event.level == "warning"


def test_journald_json_parser():
    event = parse_line('{"MESSAGE":"service failed","SYSLOG_IDENTIFIER":"demo","PRIORITY":"3"}')
    assert event.source == "json/journald"
    assert event.service == "demo"


def test_ai_prompt_redacts_secrets():
    finding = Finding("HIGH", "test", "Example", "api_key=supersecret", "Review it")
    prompt = build_safe_prompt(InvestigationContext("what happened?", [finding], ["password=hunter2"]))
    assert "supersecret" not in prompt
    assert "hunter2" not in prompt


def test_anomaly_scorer_runs():
    events = [parse_line(f"service: normal event {i}") for i in range(20)]
    assert isinstance(score_events(events), list)
