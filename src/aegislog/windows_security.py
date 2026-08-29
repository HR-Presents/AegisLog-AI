from __future__ import annotations

import re
from dataclasses import dataclass


WINDOWS_SECURITY_EVENT = re.compile(
    r"^(?P<timestamp>\S+)\s+Microsoft-Windows-Security-Auditing\[(?P<event_id>\d+)\]:\s+"
    r"(?P<level>\S+)\s*(?P<message>.*)$",
    re.IGNORECASE,
)

FIELD_PATTERNS = {
    "account": (
        re.compile(r"\bAccount Name:\s*(?P<value>[^\s]+)", re.IGNORECASE),
        re.compile(r"\bTarget User Name:\s*(?P<value>[^\s]+)", re.IGNORECASE),
        re.compile(r"\bNew Account Name:\s*(?P<value>[^\s]+)", re.IGNORECASE),
    ),
    "source_ip": (
        re.compile(r"\bSource Network Address:\s*(?P<value>[^\s]+)", re.IGNORECASE),
        re.compile(r"\bIpAddress:\s*(?P<value>[^\s]+)", re.IGNORECASE),
    ),
    "workstation": (
        re.compile(r"\bWorkstation Name:\s*(?P<value>[^\s]+)", re.IGNORECASE),
        re.compile(r"\bWorkstationName:\s*(?P<value>[^\s]+)", re.IGNORECASE),
    ),
    "process": (
        re.compile(r"\bNew Process Name:\s*(?P<value>.+?)(?=\s+(?:Token Elevation Type|Mandatory Label|Creator Process Name|Command Line):|$)", re.IGNORECASE),
    ),
}


@dataclass(frozen=True)
class WindowsSecurityEvent:
    event_id: int
    timestamp: str
    message: str
    account: str | None = None
    source_ip: str | None = None
    workstation: str | None = None
    process: str | None = None


@dataclass(frozen=True)
class SecuritySignal:
    severity: str
    category: str
    title: str
    evidence: str
    recommendation: str


EVENT_CONTEXT: dict[int, tuple[str, str, str, str]] = {
    4625: (
        "MEDIUM", "authentication", "Windows failed logon",
        "Review the target account, source address/workstation, logon type, and nearby successful logons.",
    ),
    4672: (
        "MEDIUM", "privilege", "Special privileges assigned to a new logon",
        "Confirm the privileged account and correlate this session with process creation and administrative activity.",
    ),
    4688: (
        "INFO", "process", "Windows process creation recorded",
        "Review the process path, parent process, account, and command line when process auditing is enabled.",
    ),
    4720: (
        "HIGH", "account", "Windows user account created",
        "Validate that the new account was authorized and review the actor, target account, and subsequent group membership changes.",
    ),
    4728: (
        "HIGH", "privilege", "Member added to a privileged/global security group",
        "Validate the membership change and review the initiating account and affected group.",
    ),
    4732: (
        "HIGH", "privilege", "Member added to a local security group",
        "Validate the local group membership change, especially for Administrators or other privileged groups.",
    ),
    4740: (
        "MEDIUM", "authentication", "Windows account lockout",
        "Review repeated failed logons for the locked account and correlate the caller computer or source system.",
    ),
    1102: (
        "CRITICAL", "audit", "Windows Security audit log was cleared",
        "Treat this as high-priority evidence: identify the account that cleared the log and preserve surrounding telemetry.",
    ),
}


def _field(message: str, name: str) -> str | None:
    for pattern in FIELD_PATTERNS[name]:
        match = pattern.search(message)
        if match:
            value = match.group("value").strip().strip(".,;")
            if value and value not in {"-", "::1", "127.0.0.1"}:
                return value
    return None


def parse_windows_security_line(line: str) -> WindowsSecurityEvent | None:
    match = WINDOWS_SECURITY_EVENT.match(line.strip())
    if not match:
        return None
    message = match.group("message").strip()
    return WindowsSecurityEvent(
        event_id=int(match.group("event_id")),
        timestamp=match.group("timestamp"),
        message=message,
        account=_field(message, "account"),
        source_ip=_field(message, "source_ip"),
        workstation=_field(message, "workstation"),
        process=_field(message, "process"),
    )


def signal_for_event(event: WindowsSecurityEvent) -> SecuritySignal | None:
    context = EVENT_CONTEXT.get(event.event_id)
    if context is None:
        return None
    severity, category, title, recommendation = context
    parts = [f"Event ID {event.event_id}"]
    if event.account:
        parts.append(f"account={event.account}")
    if event.source_ip:
        parts.append(f"source_ip={event.source_ip}")
    if event.workstation:
        parts.append(f"workstation={event.workstation}")
    if event.process:
        parts.append(f"process={event.process}")
    parts.append(event.message[:300])
    return SecuritySignal(severity, category, title, " | ".join(parts), recommendation)
