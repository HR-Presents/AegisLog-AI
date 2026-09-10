from pathlib import Path

from aegislog.engine import analyze_file
from aegislog.streaming import analyze_stream


def _signature(findings):
    return [(item.severity, item.category, item.title, item.evidence) for item in findings]


def test_streaming_findings_are_independent_of_chunk_size(tmp_path: Path) -> None:
    path = tmp_path / "auth.log"
    lines = [
        f"2026-09-10T10:00:{second:02d}Z app sshd: Failed password for root from 203.0.113.7 port 22"
        for second in range(6)
    ]
    lines += [
        "2026-09-10T10:01:00Z api: ERROR database connection timeout",
        "2026-09-10T10:01:01Z host firewall: UFW BLOCK SRC=198.51.100.9 DST=192.0.2.2",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    baseline = analyze_stream(path, chunk_size=1)
    for chunk_size in (2, 3, 5, 100):
        candidate = analyze_stream(path, chunk_size=chunk_size)
        assert _signature(candidate.findings) == _signature(baseline.findings)
        assert candidate.severities == baseline.severities
        assert candidate.lines == baseline.lines


def test_streaming_matches_full_file_for_rfc3164_with_year_hint(tmp_path: Path) -> None:
    path = tmp_path / "auth.log"
    lines = [
        f"Sep 10 10:00:{second:02d} web01 sshd: Failed password for root from 203.0.113.8 port 22"
        for second in range(6)
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    _, full_findings = analyze_file(path, timestamp_year_hint=2026)
    streamed = analyze_stream(path, chunk_size=2, timestamp_year_hint=2026)

    assert _signature(streamed.findings) == _signature(full_findings)
    assert any("brute-force" in item.title.lower() for item in streamed.findings)
    assert any("window=300s" in item.evidence for item in streamed.findings)


def test_streaming_year_hint_rejects_invalid_year(tmp_path: Path) -> None:
    path = tmp_path / "auth.log"
    path.write_text("Sep 10 10:00:00 web01 sshd: Failed password for root from 203.0.113.8\n", encoding="utf-8")

    try:
        analyze_stream(path, timestamp_year_hint=42)
    except ValueError as exc:
        assert "four-digit year" in str(exc)
    else:
        raise AssertionError("invalid timestamp year hint should be rejected")
