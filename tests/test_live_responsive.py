from pathlib import Path

from rich.console import Console

from aegislog.multisource import (
    MultiSourceState,
    _alerts_table as multi_alerts_table,
    _summary_table as multi_summary_table,
    render_multisource,
)
from aegislog.realtime import (
    RealtimeState,
    _recent_table,
    _summary_table as realtime_summary_table,
    render_realtime,
)


def _render(value, width: int) -> str:
    console = Console(record=True, force_terminal=False, width=width)
    console.print(value)
    return console.export_text()


def _assert_lines_fit(output: str, width: int) -> None:
    assert all(len(line) <= width for line in output.splitlines())


def test_realtime_summary_collapses_on_narrow_terminal() -> None:
    output = _render(realtime_summary_table([("Metric", "42", "context")], 40), 40)
    assert "Value / Context" in output
    assert "42" in output and "context" in output
    _assert_lines_fit(output, 40)


def test_realtime_summary_keeps_wide_layout() -> None:
    output = _render(realtime_summary_table([("Metric", "42", "context")], 100), 100)
    assert "Value" in output and "Context" in output
    assert "Value / Context" not in output
    _assert_lines_fit(output, 100)


def test_realtime_findings_use_single_column_when_narrow() -> None:
    state = RealtimeState(source="example.log")
    output = _render(_recent_table([], state.profile, 40), 40)
    assert "Finding" in output
    assert "Severity" not in output
    _assert_lines_fit(output, 40)


def test_multisource_summary_collapses_on_narrow_terminal() -> None:
    rows = [("Events", "10", "events ingested", "bold white")]
    output = _render(multi_summary_table(rows, 40), 40)
    assert "Value / Context" in output
    _assert_lines_fit(output, 40)


def test_multisource_alerts_use_single_column_when_narrow() -> None:
    state = MultiSourceState(sources=(Path("a.log"), Path("b.log")))
    output = _render(multi_alerts_table(state, 40), 40)
    assert "Alert" in output
    assert "Severity" not in output
    _assert_lines_fit(output, 40)


def test_live_headers_use_aegislog_without_ai_branding(monkeypatch) -> None:
    class Size:
        columns = 80

    def fake_size(_fallback):
        return Size()

    monkeypatch.setattr("aegislog.realtime.shutil.get_terminal_size", fake_size)
    monkeypatch.setattr("aegislog.multisource.shutil.get_terminal_size", fake_size)

    realtime_output = _render(render_realtime(RealtimeState(source="example.log")), 80)
    multisource_state = MultiSourceState(sources=(Path("a.log"), Path("b.log")))
    multi_output = _render(render_multisource(multisource_state), 80)

    assert "AEGISLOG AI" not in realtime_output
    assert "AEGISLOG AI" not in multi_output
    assert "AEGISLOG" in realtime_output
    assert "AEGISLOG" in multi_output
