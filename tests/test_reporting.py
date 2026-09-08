from __future__ import annotations

import re
from pathlib import Path

from aegislog.anomaly import Anomaly
from aegislog.dashboard import DashboardData
from aegislog.engine import Finding
from aegislog.incidents import Incident
from aegislog.reporting import build_html_report, write_html_report


def _data(source: str = "/tmp/prod-auth.log") -> DashboardData:
    return DashboardData(
        source=source,
        lines=42,
        findings=(
            Finding(
                "HIGH",
                "authentication",
                "Repeated <script>alert(1)</script> failures",
                "user=admin & source=203.0.113.10",
                "Review authentication history & rotate exposed credentials.",
            ),
            Finding(
                "MEDIUM",
                "network",
                "Firewall activity",
                'src="198.51.100.7" port=445',
                "Review repeated sources and destination ports.",
            ),
        ),
        anomalies=(Anomaly(74.2, "sshd:error", "Rare concerning event class: 1/42 total events"),),
        incidents=(
            Incident(
                id="abcdef123456",
                category="authentication",
                severity="HIGH",
                count=2,
                title="Authentication attack pattern",
                evidence=("failed <img src=x onerror=alert(1)>", "failed password for admin"),
            ),
        ),
        levels={"ERROR": 9, "WARNING": 3},
        services={"sshd": 10, "firewall": 2},
        categories={"authentication": 1, "network": 1},
        severities={"HIGH": 1, "MEDIUM": 1},
    )


def test_html_report_is_self_contained_and_analyst_oriented() -> None:
    html = build_html_report(_data())

    for text in (
        "Security Investigation Report",
        "Investigation record",
        "Case reference",
        "Executive Summary",
        "Assessment",
        "Recommended Triage",
        "Incident Queue",
        "Findings and Recommendations",
        "Anomaly Signals",
        "Observed Distribution",
        "Analysis Profile",
        "Evidence limitations",
        "LOCAL / READ-ONLY",
        "REMOTE AI NOT REQUIRED",
        "Print / Save PDF",
    ):
        assert text in html

    for anchor in (
        "#executive",
        "#triage",
        "#incidents",
        "#findings",
        "#anomalies",
        "#telemetry",
        "#method",
    ):
        assert anchor in html

    assert "@media print" in html
    assert "window.print()" in html
    assert 'src="http://' not in html
    assert 'src="https://' not in html
    assert 'href="http://' not in html
    assert 'href="https://' not in html
    assert "@import" not in html
    assert "<script src=" not in html


def test_html_report_has_stable_case_reference_for_same_snapshot() -> None:
    first = build_html_report(_data())
    second = build_html_report(_data())
    pattern = re.compile(r"AL-[A-F0-9]{10}")
    first_ids = pattern.findall(first)
    second_ids = pattern.findall(second)
    assert first_ids
    assert first_ids[0] == second_ids[0]


def test_html_report_escapes_retained_evidence() -> None:
    html = build_html_report(_data("/tmp/prod<auth>.log"))

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<img src=x onerror=alert(1)>" not in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "user=admin &amp; source=203.0.113.10" in html
    assert "prod&lt;auth&gt;.log" in html


def test_html_report_orders_triage_by_severity() -> None:
    html = build_html_report(_data())
    high_position = html.index("Review authentication history")
    medium_position = html.index("Review repeated sources")
    assert high_position < medium_position


def test_empty_report_has_clear_empty_states() -> None:
    data = DashboardData(
        source="/tmp/quiet.log",
        lines=0,
        findings=(),
        anomalies=(),
        incidents=(),
        levels={},
        services={},
        categories={},
        severities={},
    )
    html = build_html_report(data)

    assert "Current posture" in html
    assert ">CLEAR<" in html
    assert "No immediate rule-backed remediation items were generated." in html
    assert "No correlated incidents were recorded." in html
    assert "No rule-backed findings were recorded." in html
    assert "No rare concerning event classes were recorded." in html
    assert "No critical, high, or medium rule-backed findings were retained" in html


def test_write_html_report_uses_safe_predictable_filename(tmp_path: Path) -> None:
    target = write_html_report(_data("/tmp/prod auth?.log"), output_dir=tmp_path)

    assert target == tmp_path / "prod-auth-aegislog-report.html"
    assert target.is_file()
    html = target.read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert "prod auth?.log" in html
