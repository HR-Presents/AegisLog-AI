from pathlib import Path

from aegislog.realtime import RealtimeState, read_new_lines, render_realtime


def test_realtime_state_correlates_authentication_failures() -> None:
    state = RealtimeState(source="auth.log", window_size=50)
    lines = [
        f"Aug 29 12:01:0{i} demo sshd[{1000+i}]: Failed password for root from 203.0.113.7 port 22 ssh2\n"
        for i in range(1, 6)
    ]
    state.ingest(lines)

    findings = state.findings
    assert state.total_lines == 5
    assert len(findings) == 1
    assert findings[0].severity == "HIGH"
    assert findings[0].category == "authentication"


def test_realtime_state_tracks_service_and_web_findings() -> None:
    state = RealtimeState(source="security.log", window_size=50)
    state.ingest(
        [
            'Aug 29 14:22:15 server01 nginx[4410]: 203.0.113.99 - - "GET /.env HTTP/1.1" 404 153\n',
            "Aug 29 14:27:05 server01 systemd[1]: nginx.service: Failed with result 'exit-code'\n",
        ]
    )

    categories = {item.category for item in state.findings}
    assert "web" in categories
    assert "service" in categories
    assert render_realtime(state) is not None


def test_read_new_lines_reads_only_appended_content(tmp_path: Path) -> None:
    path = tmp_path / "live.log"
    path.write_text("first\n", encoding="utf-8")
    offset = path.stat().st_size
    path.write_text("first\nsecond\n", encoding="utf-8")

    lines, offset = read_new_lines(path, offset)
    assert lines == ["second\n"]

    path.write_text("rotated\n", encoding="utf-8")
    lines, _ = read_new_lines(path, offset)
    assert lines == ["rotated\n"]
