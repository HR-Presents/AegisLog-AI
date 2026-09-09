from rich.console import Console

from aegislog.commands_v11 import _analysis_complete_line
from aegislog.dashboard import DashboardData
from aegislog.engine import Finding


def test_analysis_complete_line_summarizes_result_counts() -> None:
    data = DashboardData(
        source="/tmp/sample.log",
        lines=1250,
        findings=(Finding("HIGH", "authentication", "Brute force", "evidence", "review"),),
        anomalies=(),
        incidents=(),
        levels={},
        services={},
        categories={},
        severities={"HIGH": 1},
    )
    console = Console(record=True, force_terminal=False, width=100)
    console.print(_analysis_complete_line(data))
    output = console.export_text()

    assert "ANALYSIS COMPLETE" in output
    assert "1,250 events" in output
    assert "1 findings" in output
    assert "0 incidents" in output


def test_analysis_complete_line_stays_compact() -> None:
    data = DashboardData(
        source="/tmp/empty.log",
        lines=0,
        findings=(),
        anomalies=(),
        incidents=(),
        levels={},
        services={},
        categories={},
        severities={},
    )
    console = Console(record=True, force_terminal=False, width=80)
    console.print(_analysis_complete_line(data))
    output = console.export_text().strip()

    assert "\n" not in output
    assert "0 events" in output
