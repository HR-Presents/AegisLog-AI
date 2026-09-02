from __future__ import annotations

import platform

from rich.panel import Panel
from rich.text import Text

from .native_collectors import NativeSource
from .theme import ACCENT_SOFT, MUTED, SUCCESS, WARNING


def source_state(source: NativeSource) -> tuple[str, str]:
    """Return a concise operator-facing state label and style for a native source."""
    if source.available:
        return "READY", f"bold {SUCCESS}"
    system = platform.system()
    if source.name == "windows" and system != "Windows":
        return "UNSUPPORTED HERE", MUTED
    if source.name == "journald" and system != "Linux":
        return "UNSUPPORTED HERE", MUTED
    if source.name == "docker":
        return "UNAVAILABLE", WARNING
    return "UNAVAILABLE", WARNING


def failure_guidance(source: str, detail: str) -> Panel:
    """Build read-only troubleshooting guidance for a native collection failure."""
    normalized = source.strip().lower()
    lower = detail.lower()
    text = Text()
    text.append("Source: ", style=MUTED)
    text.append(normalized or "unknown", style=ACCENT_SOFT)
    text.append("\nReason: ", style=MUTED)
    text.append(detail or "collector did not provide a reason", style="white")

    if normalized == "windows":
        if "only available on windows" in lower:
            action = "Run this source on Windows, or use journald/Docker where supported."
        elif "access" in lower or "denied" in lower or "unauthorized" in lower:
            action = "Retry with the minimum permissions required for the selected event channel; do not change host policy."
        else:
            action = "Confirm the selected channel exists and that PowerShell can read it, then retry."
    elif normalized == "journald":
        if "only available on linux" in lower:
            action = "Run this source on Linux, or choose a source supported by this host."
        else:
            action = "Confirm journalctl is available and your account can read the requested journal data."
    elif normalized == "docker":
        if "container name or id" in lower:
            action = "Provide one container name or ID with --container."
        elif "not found" in lower:
            action = "Install/enable the Docker CLI and engine, then retry without changing AegisLog permissions."
        else:
            action = "Confirm the Docker engine is running and your account can read logs for the selected container."
    else:
        action = "Choose windows, journald, or docker and retry."

    text.append("\nNext safe step: ", style=MUTED)
    text.append(action, style="white")
    text.append("\nAegisLog collectors remain read-only and do not modify host, service, firewall, or account settings.", style=MUTED)
    return Panel(text, title="Native telemetry diagnostics", title_align="left", border_style=WARNING)
