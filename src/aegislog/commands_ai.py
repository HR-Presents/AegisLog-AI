from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from .ai import InvestigationContext, build_safe_prompt, local_answer
from .engine import analyze_file
from .providers import AIResponse, ProviderError, REMOTE_AI_OPT_IN_ENV, run_provider
from .theme import ACCENT, ACCENT_SOFT, HIGH, MUTED, SUCCESS, WARNING
from .ui import bounded

console = Console()


def build_analysis_context(path: Path, question: str, *, excerpt_limit: int = 80) -> InvestigationContext:
    """Build a bounded, redaction-ready AI context from the local deterministic engine."""
    _, findings = analyze_file(path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return InvestigationContext(
        question=question,
        findings=findings,
        log_excerpt=lines[-excerpt_limit:],
    )


@contextmanager
def _remote_opt_in(enabled: bool):
    """Enable remote AI only for the duration of one explicitly approved request."""
    previous = os.environ.get(REMOTE_AI_OPT_IN_ENV)
    try:
        if enabled:
            os.environ[REMOTE_AI_OPT_IN_ENV] = "1"
        yield
    finally:
        if previous is None:
            os.environ.pop(REMOTE_AI_OPT_IN_ENV, None)
        else:
            os.environ[REMOTE_AI_OPT_IN_ENV] = previous


def answer_with_provider(
    path: Path,
    question: str,
    *,
    provider: str = "local",
    model: str = "",
    base_url: str | None = None,
    allow_remote: bool = False,
) -> AIResponse:
    """Answer one analyst question without changing deterministic detection results."""
    context = build_analysis_context(path, question)
    selected = provider.strip().lower()
    if selected == "local":
        return AIResponse("local", "deterministic", local_answer(context))

    if selected == "openai-compatible" and not allow_remote:
        raise ProviderError("Remote AI requires explicit consent for this request.")

    prompt = build_safe_prompt(context)
    with _remote_opt_in(selected == "openai-compatible" and allow_remote):
        return run_provider(selected, prompt, model, base_url)


def _result_panel(response: AIResponse) -> Panel:
    body = Text()
    body.append(response.text.strip() or "No response text was returned.", style="white")
    body.append("\n\nPROVIDER  ", style=MUTED)
    body.append(response.provider, style=f"bold {ACCENT}")
    body.append("\nMODEL     ", style=MUTED)
    body.append(response.model, style=ACCENT_SOFT)
    return Panel(
        body,
        title=Text(" AI ANALYST RESPONSE ", style=f"bold {SUCCESS}"),
        title_align="left",
        border_style=SUCCESS,
        padding=(1, 2),
        expand=True,
    )


def interactive_ai_analyst(path: Path) -> None:
    """Run the provider-backed analyst workflow inside Mission Control."""
    console.print(
        bounded(
            Panel(
                Text.from_markup(
                    "[bold]Choose how AegisLog should answer.[/bold]\n"
                    "Local uses deterministic findings only. Ollama stays on this machine. "
                    "OpenAI-compatible sends only redacted investigation context and requires explicit consent."
                ),
                title=Text(" AI PROVIDER ", style=f"bold {ACCENT}"),
                title_align="left",
                border_style=ACCENT_SOFT,
            )
        )
    )
    provider = Prompt.ask(
        "Provider",
        choices=["local", "ollama", "openai-compatible", "back"],
        default="local",
    )
    if provider == "back":
        return

    question = Prompt.ask(
        "Analyst question",
        default="What are the most important findings and what should I investigate next?",
    ).strip()
    if not question:
        return

    model = ""
    allow_remote = False
    if provider == "ollama":
        model = Prompt.ask("Ollama model", default="llama3.2").strip()
    elif provider == "openai-compatible":
        model = Prompt.ask("Model", default="gpt-4.1-mini").strip()
        consent = Prompt.ask(
            "Send redacted investigation context to the configured remote provider?",
            choices=["no", "yes"],
            default="no",
        )
        if consent != "yes":
            console.print(Text("Remote AI request cancelled. No provider request was sent.", style=WARNING))
            return
        allow_remote = True

    try:
        response = answer_with_provider(
            path,
            question,
            provider=provider,
            model=model,
            allow_remote=allow_remote,
        )
    except (ProviderError, OSError) as exc:
        console.print(
            bounded(
                Panel(
                    Text(str(exc), style="white"),
                    title=Text(" AI ANALYST UNAVAILABLE ", style=f"bold {HIGH}"),
                    border_style=HIGH,
                )
            )
        )
        return

    console.print()
    console.print(bounded(_result_panel(response)))


def ai_analyst(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    question: str = typer.Option(
        "What are the most important findings and what should I investigate next?",
        "--question",
        "-q",
        help="Defensive analyst question to answer from the selected log.",
    ),
    provider: str = typer.Option(
        "local",
        "--provider",
        help="local, ollama, or openai-compatible",
    ),
    model: str = typer.Option("", "--model", help="Provider model; defaults are provider-specific."),
    base_url: str | None = typer.Option(None, "--base-url", help="Optional provider endpoint override."),
    allow_remote: bool = typer.Option(
        False,
        "--allow-remote",
        help="Explicitly consent to sending redacted context to a remote provider for this request.",
    ),
) -> None:
    """Ask the optional AI analyst about deterministic AegisLog findings."""
    selected = provider.strip().lower()
    if selected not in {"local", "ollama", "openai-compatible"}:
        raise typer.BadParameter("provider must be local, ollama, or openai-compatible")
    if selected == "ollama" and not model:
        model = "llama3.2"
    if selected == "openai-compatible" and not model:
        model = "gpt-4.1-mini"

    try:
        response = answer_with_provider(
            path,
            question,
            provider=selected,
            model=model,
            base_url=base_url,
            allow_remote=allow_remote,
        )
    except ProviderError as exc:
        console.print(Text(str(exc), style=HIGH))
        raise typer.Exit(code=2) from exc

    console.print(bounded(_result_panel(response)))
