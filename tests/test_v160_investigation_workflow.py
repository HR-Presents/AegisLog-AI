from __future__ import annotations

from rich.console import Console

from aegislog.investigation import InvestigationIncident, TimelineEvent
from aegislog.investigation_ux import incident_triage_panel, triage_priority


def _incident(*, severity: str = "HIGH", confidence: int = 91, entities: tuple[str, ...] = ("192.0.2.10",)) -> InvestigationIncident:
    return InvestigationIncident(
        id="INC-12345678",
        severity=severity,
        confidence=confidence,
        category="authentication",
        title="Suspicious authentication activity",
        findings=(),
        entities=entities,
        timeline=(
            TimelineEvent(
                order=1,
                timestamp="12:00:00",
                service="sshd",
                level="WARNING",
                summary="Repeated failed authentication",
                entities=entities,
            ),
        ),
    )


def _render(renderable: object) -> str:
    console = Console(record=True, width=180)
    console.print(renderable)
    return console.export_text()


def test_high_confidence_high_severity_is_urgent_review() -> None:
    priority, _ = triage_priority(_incident())
    assert priority == "Urgent review"


def test_lower_signal_incident_stays_routine() -> None:
    priority, _ = triage_priority(_incident(severity="LOW", confidence=55, entities=()))
    assert priority == "Routine review"


def test_triage_panel_is_evidence_led_and_non_attributing() -> None:
    output = _render(incident_triage_panel(_incident()))
    assert "Analyst triage" in output
    assert "Priority: Urgent review" in output
    assert "Confidence: 91%" in output
    assert "Validate the associated entities" in output
    assert "not proof of compromise, attribution, or attacker intent" in output
