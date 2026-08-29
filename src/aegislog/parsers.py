from __future__ import annotations

import json
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    raw: str
    source: str = "generic"
    level: str | None = None
    service: str | None = None
    message: str = ""


NGINX = re.compile(r'(?P<ip>\S+) \S+ \S+ \[[^]]+\] "(?P<method>\S+) (?P<path>\S+)[^"]*" (?P<status>\d{3})')
SYSLOG = re.compile(r"^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\S+\s+(?P<service>[\w.-]+)(?:\[\d+\])?:\s+(?P<message>.*)$")
WINDOWS_EVENT = re.compile(
    r"^(?P<timestamp>\S+)\s+(?P<provider>[\w.(){}\-/ ]+)\[(?P<event_id>\d+)\]:\s+"
    r"(?P<level>CRITICAL|ERROR|WARNING|WARN|INFORMATION|INFO|VERBOSE)\s*(?P<message>.*)$",
    re.IGNORECASE,
)
WEB_REQUEST = re.compile(r'(?P<ip>(?:\d{1,3}\.){3}\d{1,3}).*?"(?P<method>[A-Z]+)\s+(?P<path>\S+).*?"\s+(?P<status>\d{3})')

PRIORITY_LEVELS = {
    "0": "critical",
    "1": "critical",
    "2": "critical",
    "3": "error",
    "4": "warning",
    "5": "notice",
    "6": "info",
    "7": "debug",
}

WINDOWS_LEVELS = {
    "critical": "critical",
    "error": "error",
    "warning": "warning",
    "warn": "warning",
    "information": "info",
    "info": "info",
    "verbose": "debug",
}


def _infer_level(message: str) -> str | None:
    text = message.lower()
    if re.search(r"\b(critical|crit|fatal|panic|emergency)\b", text):
        return "critical"
    if re.search(r"\b(error|failed|failure|segfault|denied|timeout|blocked?)\b", text):
        return "error"
    if re.search(r"\b(warning|warn)\b", text):
        return "warning"
    if re.search(r"\b(info|started|accepted|completed|restored|success(?:ful(?:ly)?)?)\b", text):
        return "info"
    return None


def _web_level(status: int) -> str:
    return "error" if status >= 500 else "warning" if status >= 400 else "info"


def parse_line(line: str) -> Event:
    raw = line.rstrip("\n")
    stripped = raw.strip()
    if not stripped:
        return Event(raw=raw, message="")

    if stripped.startswith("{"):
        try:
            obj = json.loads(stripped)
            message = str(obj.get("MESSAGE") or obj.get("message") or stripped)
            service = obj.get("SYSLOG_IDENTIFIER") or obj.get("_SYSTEMD_UNIT") or obj.get("service")
            priority = str(obj.get("PRIORITY") or "")
            level_value = str(obj.get("level") or "").lower()
            level = PRIORITY_LEVELS.get(priority) or level_value or _infer_level(message)
            return Event(raw=raw, source="json/journald", level=level or None, service=service, message=message)
        except json.JSONDecodeError:
            pass

    match = WINDOWS_EVENT.match(stripped)
    if match:
        provider = match.group("provider").strip()
        level = WINDOWS_LEVELS.get(match.group("level").lower())
        message = match.group("message").strip()
        return Event(raw=raw, source="windows", level=level or _infer_level(message), service=provider, message=message)

    match = NGINX.search(stripped)
    if match:
        status = int(match.group("status"))
        return Event(raw=raw, source="web", level=_web_level(status), service="http", message=stripped)

    match = SYSLOG.match(stripped)
    if match:
        service = match.group("service")
        message = match.group("message")
        web = WEB_REQUEST.search(message)
        if web:
            return Event(raw=raw, source="web", level=_web_level(int(web.group("status"))), service=service, message=message)
        return Event(raw=raw, source="syslog", level=_infer_level(message), service=service, message=message)

    return Event(raw=raw, level=_infer_level(stripped), message=stripped)
