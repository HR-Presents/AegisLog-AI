from aegislog.anomaly import score_events
from aegislog.engine import analyze_lines
from aegislog.parsers import parse_line


def test_syslog_parser_extracts_service_and_level():
    event = parse_line("Aug 29 14:23:31 server01 api[4512]: ERROR database connection timeout after 30 seconds")
    assert event.source == "syslog"
    assert event.service == "api"
    assert event.level == "error"


def test_syslog_web_request_gets_web_source_and_warning_level():
    event = parse_line('Aug 29 14:22:15 server01 nginx[4410]: 203.0.113.99 - - "GET /.env HTTP/1.1" 404 153')
    assert event.source == "web"
    assert event.service == "nginx"
    assert event.level == "warning"


def test_auth_failures_are_correlated_not_duplicated():
    lines = [f"Aug 29 14:20:0{i} server01 sshd[42{i}]: Failed password for root from 203.0.113.45 port 5123{i} ssh2" for i in range(1, 6)]
    findings = analyze_lines(lines)
    auth = [item for item in findings if item.category == "authentication"]
    assert len(auth) == 1
    assert auth[0].severity == "HIGH"
    assert "5 authentication failures" in auth[0].evidence


def test_suspicious_web_probe_and_firewall_block_are_detected():
    findings = analyze_lines([
        'Aug 29 14:22:15 server01 nginx[4410]: 203.0.113.99 - - "GET /.env HTTP/1.1" 404 153',
        "Aug 29 14:25:11 server01 kernel: [UFW BLOCK] IN=eth0 SRC=198.51.100.77 DST=192.0.2.10 PROTO=TCP SPT=45522 DPT=22",
    ])
    categories = {item.category for item in findings}
    assert "web" in categories
    assert "network" in categories


def test_anomaly_scoring_ignores_rare_info_noise():
    events = [parse_line(f"Aug 29 14:00:{i:02d} server01 api[1]: INFO request completed successfully") for i in range(10)]
    events.append(parse_line("Aug 29 14:01:01 server01 cron[2]: INFO scheduled backup completed successfully"))
    assert score_events(events) == []
