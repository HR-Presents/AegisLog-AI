from __future__ import annotations

from rich.console import Console

from aegislog.dashboard import DashboardData, render_dashboard
from aegislog.incidents import Incident


def test_dashboard_surfaces_incident_id_and_real_commands() -> None:
    data = DashboardData(
        source="sample.log",
        lines=1,
        findings=(),
        anomalies=(),
        incidents=(Incident(id="abcdef123456", category="authentication", severity="HIGH", count=2, title="Possible brute-force activity", evidence=()),),
        levels={"ERROR": 1},
        services={"sshd": 1},
        categories={},
        severities={"HIGH": 1},
    )
    console = Console(record=True, width=160)
    console.print(render_dashboard(data))
    output = console.export_text()

    assert "INC-ABCDEF12" in output
    assert "incidents <file>" in output
    assert "investigate <file> INC-ABCDEF12" in output
    assert "explain <file> INC-ABCDEF12" in output
    assert " incident`" not in output
