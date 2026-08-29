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
    ("HIGH", "privilege", re.compile(r"sudo:.*(authentication failure|incorrect password)|user NOT in sudoers", re.I), "Suspicious privilege activity", "Review sudo history, account privileges, and related authentication events."),
    ("HIGH", "web", re.compile(r"(?:union(?:%20|\s)+select|\.\./|/etc/passwd|<script|%3cscript|/\.env(?:\s|\?|$)|/wp-login\.php(?:\s|\?|$))", re.I), "Suspicious web probing detected", "Review the source address, requested endpoint, application logs, and edge/WAF controls."),
    ("MEDIUM", "network", re.compile(r"\bUFW BLOCK\b|\bfirewall\b.*\b(?:block|drop|deny)\b", re.I), "Firewall blocked inbound activity", "Review repeated sources and destination ports; confirm the traffic matches expected exposure."),
    ("MEDIUM", "service", re.compile(r"segfault|panic|fatal|crash|out of memory|oom-killer|service:\s+Failed|Failed with result", re.I), "Service or system failure", "Inspect surrounding events, resource pressure, and the affected service configuration."),
    ("MEDIUM", "error", re.compile(r"\berror\b|\bexception\b|\bdenied\b|\btimeout\b", re.I), "Operational error detected", "Inspect surrounding lines and the affected component for root cause."),
]

AUTH_FAILURE_RE = re.compile(r"failed password|authentication failure", re.I)
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


def _auth_finding(ip: str, count: int) -> Finding:
    if count >= 20:
        severity = "CRITICAL"
        title = f"Sustained brute-force activity from {ip}"
    elif count >= 5:
        severity = "HIGH"
        title = f"Possible brute-force activity from {ip}"
    else:
        severity = "MEDIUM"
        title = f"Repeated authentication failures from {ip}"
    return Finding(
        severity,
        "authentication",
        title,
        f"{count} authentication failure{'s' if count != 1 else ''} associated with {ip}",
        "Check whether this source later authenticated successfully; review account targets, SSH exposure, MFA, and rate limiting.",
    )


def analyze_lines(lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    auth_ips: Counter[str] = Counter()
    auth_without_ip = 0
    seen_rule_findings: set[tuple[str, str, str]] = set()

    for raw in lines:
        line = redact(raw.strip())
        if not line:
            continue

        if AUTH_FAILURE_RE.search(line):
            ips = IP_RE.findall(line)
            if ips:
                for ip in ips:
                    auth_ips[ip] += 1
            else:
                auth_without_ip += 1
            # Authentication failures are correlated below so that a burst is
            # represented as one meaningful finding instead of many duplicates.
            continue

        for severity, category, pattern, title, recommendation in RULES:
            if pattern.search(line):
                key = (category, title, line)
                if key not in seen_rule_findings:
                    findings.append(Finding(severity, category, title, line[:500], recommendation))
                    seen_rule_findings.add(key)
                break

    for ip, count in sorted(auth_ips.items(), key=lambda item: (-item[1], item[0])):
        findings.insert(0, _auth_finding(ip, count))

    if auth_without_ip:
        findings.append(Finding(
            "HIGH" if auth_without_ip >= 5 else "MEDIUM",
            "authentication",
            "Repeated authentication failures",
            f"{auth_without_ip} authentication failure{'s' if auth_without_ip != 1 else ''} without a parsed source address",
            "Review surrounding authentication logs and correlate accounts, hosts, and source addresses.",
        ))

    return findings


def analyze_file(path: Path) -> tuple[int, list[Finding]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()
    return len(lines), analyze_lines(lines)
