from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

from aegislog.commands_v15 import _analyst_workflow, _command_name, _investigation_next_actions
from aegislog.investigation import InvestigationIncident


def _incident() -> InvestigationIncident:
    return InvestigationIncident(
        id="INC-ABCDEF12",
        severity="HIGH",
        confidence=91,
        category="authentication",
        title="Possible brute-force activity",
        findings=(),
        entities=("192.0.2.10", "user:alice"),
        timeline=(),
    )


def _render(renderable: object) -> str:
    console = Console(record=True, width=180)
    console.print(renderable)
    return console.export_text()


def test_incident_workflow_surfaces_ordered_next_commands() -> None:
    output = _render(_analyst_workflow(Path("sample log.log"), _incident()))

    assert "Analyst workflow" in output
    assert 'aegislog investigate "sample log.log" INC-ABCDEF12' in output
    assert 'aegislog explain "sample log.log" INC-ABCDEF12' in output
    assert 'aegislog save-investigation "sample log.log" INC-ABCDEF12' in output
    assert 'aegislog intel-entities "sample log.log"' in output
    assert 'aegislog mitre "sample log.log"' in output
    assert "not proof of compromise or attribution" in output


def test_investigation_next_actions_remain_incident_specific() -> None:
    output = _render(_investigation_next_actions(Path("auth.log"), _incident()))

    assert "Next analyst actions" in output
    assert "aegislog explain auth.log INC-ABCDEF12" in output
    assert "aegislog save-investigation auth.log INC-ABCDEF12" in output
    assert "aegislog intel-entities auth.log" in output
    assert "aegislog mitre auth.log" in output


def test_runtime_command_uses_windows_executable_when_frozen(monkeypatch) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert _command_name() == "AegisLog.exe"
