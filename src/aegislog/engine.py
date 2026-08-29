from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .sanitize import terminal_safe


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    title: str
    evidence: str
    recommendation: str


RULES = [
    ("CRITICAL", "authentication", re.compile(r"failed password|authentication failure", re.I), "Authentication failures detected", "Review source addresses and successful logins; harden authentication and rate limits."),
    ("HIGH", "privilege", re.compile(r"sudo:.*(authentication failure|incorrect password)|user NOT in sudoers", re.I), "Suspicious privilege activity", "Review sudo history, account privileges, and related authentication events."),
    ("HIGH", "web", re.compile(r"(?:union(?:%20|\s)+select|\.\./|/etc/passwd|<script|%3cscript)", re.I), "Suspicious web request pattern", "Review the request context, application logs, WAF controls, and affected endpoint."),
    ("MEDIUM", "service", re.compile(r"segfault|panic|fatal|crash|out of memory|oom-killer", re.I), "Service or system failure", "Inspect surrounding events, resource pressure, and the affected service configuration."),
    ("MEDIUM", "error", re.compile(r"\berror\b|\bexception\b|\bdenied\b|\btimeout\b", re.I), "Operational error detected", "Inspect surrounding lines and the affected component for root cause."),
]

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SECRET_PATTERNS = [
    re.compile(r"(?i)(password|passwd|token|api[_-]?key|secret)\s*[=:]\s*[^\s,;]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
]


def redact(text: str) -> str:
    text = terminal_safe(text)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda m: f"{m.group(1)}=[REDACTED]" if m.lastindex else "[REDACTED]", text)
    return text


def analyze_lines(lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    auth_ips: Counter[str] = Counter()

    for raw in lines:
        line = redact(raw.strip())
        if not line:
            continue
        if re.search(r"failed password|authentication failure", line, re.I):
            for ip in IP_RE.findall(line):
                auth_ips[ip] += 1
        for severity, category, pattern, title, recommendation in RULES:
            if pattern.search(line):
                findings.append(Finding(severity, category, title, line[:500], recommendation))
                break

    for ip, count in auth_ips.items():
        if count >= 5:
            findings.insert(0, Finding(
                "CRITICAL" if count >= 20 else "HIGH",
                "authentication",
                f"Possible brute-force activity from {ip}",
                f"{count} authentication failures associated with {ip}",
                "Check whether this source later authenticated successfully; review SSH exposure and rate limiting.",
            ))
    return findings


def analyze_file(path: Path) -> tuple[int, list[Finding]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()
    return len(lines), analyze_lines(lines)
