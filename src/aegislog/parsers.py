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
SYSLOG = re.compile(r"^[A-Z][a-z]{2}\s+\d+\s+\S+\s+\S+\s+(?P<service>[\w.-]+)(?:\[\d+\])?:\s+(?P<message>.*)$")


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
            level = str(obj.get("PRIORITY") or obj.get("level") or "") or None
            return Event(raw=raw, source="json/journald", level=level, service=service, message=message)
        except json.JSONDecodeError:
            pass

    match = NGINX.search(stripped)
    if match:
        status = int(match.group("status"))
        level = "error" if status >= 500 else "warning" if status >= 400 else "info"
        return Event(raw=raw, source="web", level=level, service="http", message=stripped)

    match = SYSLOG.match(stripped)
    if match:
        return Event(raw=raw, source="syslog", service=match.group("service"), message=match.group("message"))

    return Event(raw=raw, message=stripped)
