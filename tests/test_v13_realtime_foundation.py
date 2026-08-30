from pathlib import Path

from aegislog.multisource import MultiSourceState, initial_cursors, poll_sources
from aegislog.realtime import RealtimeState, initial_cursor, read_new_lines_cursor


def test_byte_cursor_handles_multibyte_utf8_append(tmp_path: Path) -> None:
    path = tmp_path / "unicode.log"
    path.write_text("service: café ready\n", encoding="utf-8")
    cursor = initial_cursor(path, from_start=False)
    with path.open("a", encoding="utf-8") as handle:
        handle.write("service: naïve warning\n")
    lines, cursor = read_new_lines_cursor(path, cursor)
    assert lines == ["service: naïve warning\n"]
    assert cursor.offset == path.stat().st_size


def test_cursor_detects_replaced_file_even_when_new_file_is_larger(tmp_path: Path) -> None:
    path = tmp_path / "rotating.log"
    path.write_text("old line\n", encoding="utf-8")
    cursor = initial_cursor(path, from_start=False)
    path.unlink()
    path.write_text("new file first\nnew file second\n", encoding="utf-8")
    lines, cursor = read_new_lines_cursor(path, cursor)
    assert lines == ["new file first\n", "new file second\n"]
    assert cursor.offset == path.stat().st_size


def test_realtime_seen_fingerprints_expire_without_duplicating_recent_rows() -> None:
    state = RealtimeState(source="web.log", window_size=50, alert_ttl_seconds=5)
    line = 'Aug 29 12:00:00 host nginx[1]: 203.0.113.2 - - "GET /.env HTTP/1.1" 404 153\n'
    state.ingest([line], now=10.0)
    assert len(state._seen_fingerprints) == 1
    state._expire_seen(20.0)
    assert not state._seen_fingerprints

    state.ingest([line], now=20.0)
    assert len(state.recent_findings) == 1


def test_multisource_alert_uses_evidence_source(tmp_path: Path) -> None:
    auth = tmp_path / "auth.log"
    web = tmp_path / "web.log"
    auth.write_text("", encoding="utf-8")
    web.write_text("", encoding="utf-8")
    state = MultiSourceState((auth, web), window_size=100)
    line = 'Aug 29 12:00:00 host nginx[1]: 203.0.113.2 - - "GET /.env HTTP/1.1" 404 153\n'
    state.ingest(web, [line], now=10.0)
    assert state.alerts
    assert state.alerts[0].source == "web.log"


def test_multisource_poll_detects_rotation(tmp_path: Path) -> None:
    first = tmp_path / "first.log"
    second = tmp_path / "second.log"
    first.write_text("old\n", encoding="utf-8")
    second.write_text("", encoding="utf-8")
    paths = (first, second)
    cursors = initial_cursors(paths, from_start=False)
    first.unlink()
    first.write_text("replacement one\nreplacement two\n", encoding="utf-8")
    batches, cursors = poll_sources(paths, cursors)
    found = {path.name: lines for path, lines in batches}
    assert found["first.log"] == ["replacement one\n", "replacement two\n"]
    assert cursors[first].offset == first.stat().st_size
