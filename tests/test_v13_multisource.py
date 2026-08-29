from pathlib import Path

from rich.console import Console

from aegislog.multisource import MultiSourceState, initial_offsets, poll_sources, render_multisource


def test_multisource_correlates_auth_across_files(tmp_path: Path):
    auth1 = tmp_path / "auth1.log"
    auth2 = tmp_path / "auth2.log"
    auth1.write_text("", encoding="utf-8")
    auth2.write_text("", encoding="utf-8")
    state = MultiSourceState((auth1, auth2), window_size=100)
    lines1 = [f"Aug 29 12:00:0{i} host sshd[1]: Failed password for root from 203.0.113.9 port 22 ssh2\n" for i in range(3)]
    lines2 = [f"Aug 29 12:00:1{i} host sshd[2]: Failed password for admin from 203.0.113.9 port 22 ssh2\n" for i in range(3)]
    state.ingest(auth1, lines1)
    state.ingest(auth2, lines2)
    assert any(item.category == "authentication" and item.severity == "HIGH" for item in state.findings)
    assert state.source_counts["auth1.log"] == 3
    assert state.source_counts["auth2.log"] == 3


def test_multisource_alert_feed_deduplicates(tmp_path: Path):
    source = tmp_path / "web.log"
    source.write_text("", encoding="utf-8")
    state = MultiSourceState((source, tmp_path / "other.log"), window_size=100)
    line = 'Aug 29 12:00:00 host nginx[1]: 203.0.113.2 - - "GET /.env HTTP/1.1" 404 153\n'
    state.ingest(source, [line])
    count = len(state.alerts)
    state.ingest(source, [line])
    assert len(state.alerts) == count


def test_poll_sources_reads_appended_data(tmp_path: Path):
    first = tmp_path / "first.log"; second = tmp_path / "second.log"
    first.write_text("old\n", encoding="utf-8"); second.write_text("", encoding="utf-8")
    paths = (first, second)
    offsets = initial_offsets(paths, from_start=False)
    with first.open("a", encoding="utf-8") as handle: handle.write("new one\n")
    with second.open("a", encoding="utf-8") as handle: handle.write("new two\n")
    batches, offsets = poll_sources(paths, offsets)
    found = {path.name: lines for path, lines in batches}
    assert found["first.log"] == ["new one\n"]
    assert found["second.log"] == ["new two\n"]
    assert all(offsets[path] == path.stat().st_size for path in paths)


def test_multisource_dashboard_renders(tmp_path: Path):
    first = tmp_path / "a.log"; second = tmp_path / "b.log"
    first.write_text("", encoding="utf-8"); second.write_text("", encoding="utf-8")
    state = MultiSourceState((first, second), window_size=100)
    state.ingest(first, ["Aug 29 12:00:00 host api[1]: ERROR database timeout\n"])
    console = Console(record=True, width=180)
    console.print(render_multisource(state))
    output = console.export_text()
    assert "MULTI-SOURCE REAL-TIME SOC" in output
    assert "Live security alert feed" in output
    assert "Events by source" in output
