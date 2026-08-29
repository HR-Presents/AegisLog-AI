from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class Collection:
    source: str
    lines: list[str]


class CollectorError(RuntimeError):
    pass


def _run(command: list[str], timeout: int = 20) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CollectorError(str(exc)) from exc
    if result.returncode != 0:
        raise CollectorError(result.stderr.strip() or f"command exited with {result.returncode}")
    return result.stdout


def journal(lines: int = 300, unit: str | None = None) -> Collection:
    if not shutil.which("journalctl"):
        raise CollectorError("journalctl is not installed")
    command = ["journalctl", "--no-pager", "-n", str(max(1, min(lines, 5000))), "-o", "json"]
    if unit:
        command.extend(["-u", unit])
    output = _run(command)
    normalized: list[str] = []
    for raw in output.splitlines():
        try:
            obj = json.loads(raw)
            normalized.append(json.dumps(obj, separators=(",", ":")))
        except json.JSONDecodeError:
            normalized.append(raw)
    return Collection(f"journald:{unit or 'system'}", normalized)


def docker(container: str, lines: int = 300) -> Collection:
    if not shutil.which("docker"):
        raise CollectorError("docker is not installed")
    if not container or container.startswith("-"):
        raise CollectorError("invalid container name")
    output = _run(["docker", "logs", "--tail", str(max(1, min(lines, 5000))), container])
    return Collection(f"docker:{container}", output.splitlines())
