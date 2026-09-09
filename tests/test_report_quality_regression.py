from aegislog.dashboard import analyze_dashboard
from aegislog.engine import Finding
from aegislog.incidents import correlate
from aegislog.parsers import parse_line


def test_iso_service_parser_retains_level_service_and_message():
    event = parse_line(
        "2026-09-02T12:00:18Z ERROR firewall[903]: blocked inbound connection from 203.0.113.77 port=22"
    )

    assert event.source == "iso-service"
    assert event.level == "error"
    assert event.service == "firewall"
    assert event.message == "blocked inbound connection from 203.0.113.77 port=22"


def test_report_telemetry_does_not_collapse_iso_services_to_unknown(tmp_path):
    source = tmp_path / "sample.log"
    source.write_text(
        "\n".join(
            [
                "2026-09-02T12:00:18Z ERROR firewall[903]: blocked inbound connection from 203.0.113.77 port=22",
                "2026-09-02T12:00:33Z ERROR app[774]: database connection timeout service=customer-api",
                "2026-09-02T12:00:59Z ERROR sudo[1820]: guest is not in the sudoers file",
                "2026-09-02T12:01:14Z ERROR backup[1990]: backup destination temporarily unavailable",
            ]
        ),
        encoding="utf-8",
    )

    data = analyze_dashboard(source)

    assert data.services == {"firewall": 1, "app": 1, "sudo": 1, "backup": 1}
    assert all(not anomaly.key.startswith("unknown:") for anomaly in data.anomalies)


def test_unrelated_operational_errors_are_not_one_correlated_incident():
    findings = [
        Finding(
            "MEDIUM",
            "error",
            "Operational error detected",
            "2026-09-02T12:00:33Z ERROR app[774]: database connection timeout service=customer-api",
            "review",
        ),
        Finding(
            "MEDIUM",
            "error",
            "Operational error detected",
            "2026-09-02T12:01:14Z ERROR backup[1990]: backup destination temporarily unavailable",
            "review",
        ),
    ]

    assert correlate(findings) == []


def test_repeated_same_service_and_source_can_correlate():
    findings = [
        Finding(
            "MEDIUM",
            "network",
            "Firewall blocked inbound activity",
            "2026-09-02T12:00:18Z ERROR firewall[903]: blocked inbound connection from 203.0.113.77 port=22",
            "review",
        ),
        Finding(
            "MEDIUM",
            "network",
            "Firewall blocked inbound activity",
            "2026-09-02T12:01:28Z ERROR firewall[903]: blocked inbound connection from 203.0.113.77 port=22",
            "review",
        ),
    ]

    incidents = correlate(findings)

    assert len(incidents) == 1
    assert incidents[0].count == 2
    assert incidents[0].category == "network"
