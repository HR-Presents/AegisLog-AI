from pathlib import Path

from aegislog.baseline import compare
from aegislog.database import add_incidents, get_incident, list_incidents
from aegislog.exporters import html_report, markdown_report
from aegislog.incidents import Incident


def test_sqlite_incident_roundtrip(tmp_path: Path):
    db = tmp_path / "test.db"
    item = Incident(
        id="INC-1",
        category="auth",
        severity="HIGH",
        count=3,
        title="Repeated failures",
        evidence=("one", "two"),
    )
    assert add_incidents("auth.log", "2026-08-29T00:00:00+00:00", [item], db) == 1
    rows = list_incidents(path=db)
    assert rows[0]["title"] == "Repeated failures"
    assert rows[0]["category"] == "auth"
    assert rows[0]["severity"] == "HIGH"
    assert rows[0]["event_count"] == 3
    detail = get_incident(rows[0]["id"], db)
    assert detail is not None
    assert detail["evidence"] == ["one", "two"]


def test_baseline_comparison_detects_growth():
    before = ["INFO service started"]
    after = ["ERROR failed request", "ERROR failed request", "INFO service started"]
    deltas = compare(before, after)
    assert deltas
    assert any(item.current > item.baseline for item in deltas)


def test_reports_escape_untrusted_html():
    class Finding:
        severity = "HIGH"
        title = "<script>alert(1)</script>"
        category = "test"
        evidence = "<b>x</b>"
        recommendation = "review"

    md = markdown_report("sample.log", 1, [Finding()], [])
    page = html_report("sample.log", 1, [Finding()], [])
    assert "AegisLog AI Security Report" in md
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
