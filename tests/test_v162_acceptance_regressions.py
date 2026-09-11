from rich.console import Console

from aegislog.ai import InvestigationContext, build_safe_prompt
from aegislog.commands_v145 import _header, _home


def _render(renderable, *, width: int = 120) -> str:
    console = Console(record=True, width=width, color_system=None)
    console.print(renderable)
    return console.export_text()


def test_mission_control_header_omits_version_and_falcon() -> None:
    rendered = _render(_header(120))
    assert "AEGISLOG" in rendered
    assert "VERSION" not in rendered
    assert "__/\\__" not in rendered
    assert "<F>" not in rendered


def test_mission_control_brand_is_centered_wordmark_and_ascii_safe() -> None:
    rendered = _render(_header(120))
    assert "DEFENSIVE LOG INVESTIGATION" in rendered
    assert "MADE BY HR-PRESENTS" in rendered
    assert "LOCAL-FIRST  |  READ-ONLY  |  DETERMINISTIC" in rendered
    assert "STAY AHEAD" not in rendered
    assert "|---/\\_/\\---|" not in rendered
    rendered.encode("ascii")


def test_mission_control_fits_common_terminal_widths_without_horizontal_overflow() -> None:
    for width in (32, 40, 54, 64, 80, 120, 160):
        rendered = _render(_home(width), width=width)
        rendered.encode("ascii")
        lines = rendered.splitlines()
        assert lines
        assert max(len(line) for line in lines) <= width
        assert "AEGISLOG" in rendered
        assert "01" in rendered
        assert "Q EXIT" in rendered.upper()


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
