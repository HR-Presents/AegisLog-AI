from rich.console import Console

from aegislog import __version__
from aegislog.ai import InvestigationContext, build_safe_prompt
from aegislog.commands_v145 import _header


def _render(renderable) -> str:
    console = Console(record=True, width=120, color_system=None)
    console.print(renderable)
    return console.export_text()


def test_mission_control_header_uses_runtime_package_version() -> None:
    rendered = _render(_header(120))
    assert f"v{__version__}" in rendered
    assert "v1.6.1" not in rendered


def test_ai_prompt_forbids_unsupported_trust_and_confidence_claims() -> None:
    prompt = build_safe_prompt(
        InvestigationContext(
            question="What is suspicious?",
            findings=[],
            log_excerpt=["failed authentication source=203.0.113.77"],
        )
    )
    for required in (
        "Do not infer trust status",
        "Do not invent numeric confidence percentages",
        "Treat brute force, scanning, exploitation, and coordinated activity as hypotheses",
        "Recommend verification and context collection before blocking",
    ):
        assert required in prompt
