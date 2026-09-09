from pathlib import Path

import pytest
from rich.console import Console

from aegislog.commands_ai import _provider_panel, answer_with_provider, build_analysis_context
from aegislog.commands_v145 import _home
from aegislog.providers import ProviderError


def _sample_log(tmp_path: Path) -> Path:
    path = tmp_path / "auth.log"
    path.write_text(
        "\n".join(
            [
                "2026-09-07T10:00:00Z sshd: Failed password for root from 203.0.113.21 port 2200",
                "2026-09-07T10:00:10Z sshd: Failed password for root from 203.0.113.21 port 2201",
                "2026-09-07T10:00:20Z sshd: Failed password for root from 203.0.113.21 port 2202",
                "2026-09-07T10:00:30Z sshd: Failed password for root from 203.0.113.21 port 2203",
                "2026-09-07T10:00:40Z sshd: Failed password for root from 203.0.113.21 port 2204",
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_ai_analyst_is_visible_in_mission_control() -> None:
    console = Console(record=True, force_terminal=False, width=100)
    console.print(_home(100))
    output = console.export_text()

    assert "AI ANALYST" in output
    assert "A" in output
    assert "opt-in remote AI" in output


def test_ai_provider_workspace_explains_privacy_and_detection(tmp_path: Path) -> None:
    path = _sample_log(tmp_path)
    console = Console(record=True, force_terminal=False, width=100)
    console.print(_provider_panel(path))
    output = console.export_text()

    assert "auth.log" in output
    assert "LOCAL" in output
    assert "OLLAMA" in output
    assert "REMOTE" in output
    assert "redacted context only" in output
    assert "explicit consent required" in output
    assert "Always deterministic and unchanged by AI output" in output


def test_local_ai_analyst_uses_deterministic_findings(tmp_path: Path) -> None:
    path = _sample_log(tmp_path)
    response = answer_with_provider(
        path,
        "What should I investigate?",
        provider="local",
    )

    assert response.provider == "local"
    assert response.model == "deterministic"
    assert "investigative signals" in response.text


def test_remote_ai_requires_explicit_consent(tmp_path: Path) -> None:
    path = _sample_log(tmp_path)

    with pytest.raises(ProviderError, match="explicit consent"):
        answer_with_provider(
            path,
            "Summarize the findings",
            provider="openai-compatible",
            model="gpt-4.1-mini",
            allow_remote=False,
        )


def test_analysis_context_is_bounded(tmp_path: Path) -> None:
    path = tmp_path / "many.log"
    path.write_text("\n".join(f"line-{index}" for index in range(120)), encoding="utf-8")

    context = build_analysis_context(path, "question", excerpt_limit=25)

    assert len(context.log_excerpt) == 25
    assert context.log_excerpt[0] == "line-95"
    assert context.log_excerpt[-1] == "line-119"
