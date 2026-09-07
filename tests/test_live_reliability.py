from pathlib import Path

from aegislog.realtime import RealtimeState, initial_cursor, read_new_lines_cursor


def test_partial_write_is_not_emitted_until_newline(tmp_path: Path) -> None:
    path = tmp_path / "live.log"
    path.write_bytes(b"")
    cursor = initial_cursor(path, from_start=True)

    path.write_bytes(b"first partial")
    lines, cursor = read_new_lines_cursor(path, cursor)
    assert lines == []
    assert cursor.pending == b"first partial"

    with path.open("ab") as handle:
        handle.write(b" rest\nsecond\n")
    lines, cursor = read_new_lines_cursor(path, cursor)
    assert lines == ["first partial rest\n", "second\n"]
    assert cursor.pending == b""


def test_completed_line_is_not_duplicated_on_next_poll(tmp_path: Path) -> None:
    path = tmp_path / "live.log"
    path.write_bytes(b"")
    cursor = initial_cursor(path, from_start=True)
    path.write_bytes(b"one\n")

    first, cursor = read_new_lines_cursor(path, cursor)
    second, cursor = read_new_lines_cursor(path, cursor)
    assert first == ["one\n"]
    assert second == []


def test_source_loss_and_recovery_are_reported_and_recovered(tmp_path: Path) -> None:
    path = tmp_path / "live.log"
    path.write_text("old\n", encoding="utf-8")
    cursor = initial_cursor(path)
    path.unlink()

    lines, cursor = read_new_lines_cursor(path, cursor)
    assert lines == []
    assert cursor.source_available is False
    assert cursor.reset_reason == "source_missing"

    path.write_text("recovered\n", encoding="utf-8")
    lines, cursor = read_new_lines_cursor(path, cursor)
    assert lines == ["recovered\n"]
    assert cursor.source_available is True
    assert cursor.reset_reason == "source_recovered"


def test_truncation_or_replacement_restarts_from_new_content(tmp_path: Path) -> None:
    path = tmp_path / "live.log"
    path.write_text("old content that is longer\n", encoding="utf-8")
    cursor = initial_cursor(path)

    path.write_text("new\n", encoding="utf-8")
    lines, cursor = read_new_lines_cursor(path, cursor)
    assert lines == ["new\n"]
    assert cursor.reset_reason in {"source_truncated", "source_replaced"}


def test_realtime_window_is_bounded_by_bytes_and_event_count() -> None:
    state = RealtimeState(source="synthetic.log", window_size=20, max_window_bytes=80, max_line_bytes=40)
    state.ingest([f"INFO event {index:04d}\n" for index in range(1000)], now=1.0)

    assert state.total_lines == 1000
    assert state.rolling_count <= 20
    assert state.rolling_bytes <= 80
    assert state.dropped_window_lines > 0


def test_realtime_truncates_unusually_long_lines_explicitly() -> None:
    state = RealtimeState(source="synthetic.log", window_size=20, max_window_bytes=200, max_line_bytes=40)
    state.ingest(["X" * 500 + "\n"], now=1.0)

    assert state.truncated_lines == 1
    assert "[TRUNCATED]" in state.lines[0]
    assert state.rolling_bytes <= 200
