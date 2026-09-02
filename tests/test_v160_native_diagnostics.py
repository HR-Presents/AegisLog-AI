from __future__ import annotations

from rich.console import Console

from aegislog.native_collectors import NativeSource
from aegislog.native_diagnostics import failure_guidance, source_state


def _render(renderable: object) -> str:
    console = Console(record=True, width=180)
    console.print(renderable)
    return console.export_text()


def test_docker_unavailable_is_not_reported_as_wrong_os(monkeypatch) -> None:
    monkeypatch.setattr("aegislog.native_diagnostics.platform.system", lambda: "Windows")
    label, _ = source_state(NativeSource("docker", "Docker logs", False, "Docker CLI not found"))
    assert label == "UNAVAILABLE"


def test_windows_source_is_marked_unsupported_off_windows(monkeypatch) -> None:
    monkeypatch.setattr("aegislog.native_diagnostics.platform.system", lambda: "Linux")
    label, _ = source_state(NativeSource("windows", "Windows Event Logs", False, "System/Application/Security channels"))
    assert label == "UNSUPPORTED HERE"


def test_docker_failure_guidance_is_safe_and_actionable() -> None:
    output = _render(failure_guidance("docker", "provide one Docker container name or ID"))
    assert "Native telemetry diagnostics" in output
    assert "Provide one container name or ID with --container" in output
    assert "read-only" in output
    assert "do not modify host, service, firewall, or account settings" in output


def test_windows_permission_guidance_does_not_recommend_policy_changes() -> None:
    output = _render(failure_guidance("windows", "Access is denied"))
    assert "minimum permissions required" in output
    assert "do not change host policy" in output
