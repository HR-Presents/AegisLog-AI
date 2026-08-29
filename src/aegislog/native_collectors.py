from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import dataclass
from typing import Callable


class CollectorError(RuntimeError):
    """Raised when a native source cannot be read safely."""


@dataclass(frozen=True)
class NativeSource:
    name: str
    label: str
    available: bool
    detail: str


def _run(command: list[str], timeout: int = 15) -> str:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CollectorError(str(exc)) from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "collector command failed").strip()
        raise CollectorError(detail[:500])
    return result.stdout


def windows_event_logs(limit: int = 300, channel: str = "System") -> list[str]:
    if os.name != "nt":
        raise CollectorError("Windows Event Logs are only available on Windows")
    safe_channels = {"System", "Application", "Security"}
    if channel not in safe_channels:
        raise CollectorError("channel must be System, Application, or Security")
    count = max(1, min(int(limit), 2000))
    script = (
        f"Get-WinEvent -LogName '{channel}' -MaxEvents {count} -ErrorAction Stop | "
        "Select-Object TimeCreated,Id,LevelDisplayName,ProviderName,Message | ConvertTo-Json -Compress"
    )
    raw = _run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script], timeout=30).strip()
    if not raw:
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CollectorError("Windows returned invalid event data") from exc
    records = payload if isinstance(payload, list) else [payload]
    lines: list[str] = []
    for item in records:
        if not isinstance(item, dict):
            continue
        timestamp = str(item.get("TimeCreated") or "")
        level = str(item.get("LevelDisplayName") or "INFO").upper()
        provider = str(item.get("ProviderName") or "windows")
        event_id = str(item.get("Id") or "")
        message = " ".join(str(item.get("Message") or "").split())
        lines.append(f"{timestamp} {provider}[{event_id}]: {level} {message}\n")
    return lines


def journald_logs(limit: int = 300) -> list[str]:
    if platform.system() != "Linux":
        raise CollectorError("journald is only available on Linux")
    count = max(1, min(int(limit), 5000))
    raw = _run(["journalctl", "--no-pager", "-n", str(count), "-o", "short-iso"], timeout=30)
    return [line + "\n" for line in raw.splitlines() if line.strip()]


def docker_logs(container: str, limit: int = 300) -> list[str]:
    name = container.strip()
    if not name or any(ch.isspace() for ch in name):
        raise CollectorError("provide one Docker container name or ID")
    count = max(1, min(int(limit), 5000))
    raw = _run(["docker", "logs", "--timestamps", "--tail", str(count), name], timeout=30)
    return [f"docker/{name}: {line}\n" for line in raw.splitlines() if line.strip()]


def source_status() -> list[NativeSource]:
    system = platform.system()
    return [
        NativeSource("windows", "Windows Event Logs", system == "Windows", "System/Application/Security channels"),
        NativeSource("journald", "Linux journald", system == "Linux", "journalctl read-only snapshot"),
        NativeSource("docker", "Docker logs", True, "requires local Docker CLI and container access"),
    ]


def collect(source: str, *, limit: int = 300, channel: str = "System", container: str = "") -> list[str]:
    collectors: dict[str, Callable[[], list[str]]] = {
        "windows": lambda: windows_event_logs(limit=limit, channel=channel),
        "journald": lambda: journald_logs(limit=limit),
        "docker": lambda: docker_logs(container=container, limit=limit),
    }
    try:
        collector = collectors[source]
    except KeyError as exc:
        raise CollectorError(f"unknown native source: {source}") from exc
    return collector()
