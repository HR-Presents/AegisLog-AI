from pathlib import Path

from aegislog.dashboard import DashboardData
from aegislog.engine import Finding
from aegislog.incidents import Incident
from aegislog.reporting_sentrix import build_html_report, write_html_report


def _data() -> DashboardData:
    finding = Finding(
        "MEDIUM",
        "authentication",
        "Repeated authentication failures",
        "3 authentication failures from 203.0.113.7",
        "Review successful logons, MFA, and rate limiting.",
    )
    incident = Incident(
        id="abcdef123456",
        category="authentication",
        severity="MEDIUM",
        count=1,
        title="Repeated authentication failures",
        evidence=(finding.evidence,),
    )
    return DashboardData(
        source=r"C:\\Logs\\sample.log",
        lines=4,
        findings=(finding,),
        anomalies=(),
        incidents=(incident,),
        levels={"ERROR": 3, "INFO": 1},
        services={"sshd": 4},
        categories={"authentication": 1},
        severities={"MEDIUM": 1},
        raw_lines=("line one", "line two"),
    )


def test_report_uses_sentrix_style_document_structure_with_aegislog_identity() -> None:
    html = build_html_report(_data())
    for text in (
        "AEGISLOG",
        "PRESENTED BY HR-PRESENTS",
        "Investigation Report",
        "Executive Summary",
        "Investigation Overview",
        "Source Profile",
        "Visual Analytics",
        "Incidents",
        "Findings",
        "Anomalies",
        "Appendix",
        "Print / Save as PDF",
    ):
        assert text in html
    assert "Sentrix" not in html


def test_report_visuals_are_backed_by_analysis_values() -> None:
    html = build_html_report(_data())
    assert "Repeated authentication failures" in html
    assert "3 authentication failures from 203.0.113.7" in html
    assert "SSHD" in html
    assert "ERROR" in html
    assert "MEDIUM" in html
    for color in ("--primary:#16a6a1", "--violet:#7c6fd0", "--sky:#3b82c4", "--amber:#d99932", "--coral:#d85f68", "--mint:#3f9e79"):
        assert color in html


def test_report_writes_locally_without_touching_source(tmp_path: Path) -> None:
    output = write_html_report(_data(), output_dir=tmp_path)
    assert output.exists()
    assert output.name == "sample-aegislog-report.html"
    assert "Source unchanged" in output.read_text(encoding="utf-8")
