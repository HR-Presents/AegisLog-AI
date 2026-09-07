from pathlib import Path

from aegislog.dashboard import analyze_dashboard


def _auth_severities(path: Path, *, year: int | None) -> list[str]:
    data = analyze_dashboard(path, timestamp_year_hint=year)
    return [finding.severity for finding in data.findings if finding.category == "authentication"]


def test_dashboard_timestamp_year_prevents_false_cross_window_auth_correlation(tmp_path: Path):
    log = tmp_path / "archived-auth.log"
    log.write_text(
        "Sep  7 10:00:00 host sshd[1]: Failed password for root from 203.0.113.7 port 22 ssh2\n"
        "Sep  7 10:10:00 host sshd[2]: Failed password for root from 203.0.113.7 port 22 ssh2\n"
        "Sep  7 10:20:00 host sshd[3]: Failed password for root from 203.0.113.7 port 22 ssh2\n"
        "Sep  7 10:30:00 host sshd[4]: Failed password for root from 203.0.113.7 port 22 ssh2\n"
        "Sep  7 10:40:00 host sshd[5]: Failed password for root from 203.0.113.7 port 22 ssh2\n",
        encoding="utf-8",
    )

    fallback = _auth_severities(log, year=None)
    event_time = _auth_severities(log, year=2026)

    assert "HIGH" in fallback
    assert "HIGH" not in event_time
    assert event_time == ["LOW"]


def test_dashboard_timestamp_year_rejects_out_of_range_year(tmp_path: Path):
    log = tmp_path / "auth.log"
    log.write_text(
        "Sep  7 10:00:00 host sshd[1]: Failed password for root from 203.0.113.7 port 22 ssh2\n",
        encoding="utf-8",
    )

    try:
        analyze_dashboard(log, timestamp_year_hint=1969)
    except ValueError as exc:
        assert "timestamp_year_hint" in str(exc)
    else:
        raise AssertionError("out-of-range timestamp year should be rejected")
