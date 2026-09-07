from __future__ import annotations

import ipaddress
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .sanitize import redact_sensitive
from .windows_security import parse_windows_security_line, signal_for_event


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    title: str
    evidence: str
    recommendation: str


RULES = [
    ("HIGH", "privilege", re.compile(r"sudo:.*(authentication failure|incorrect password)|user NOT in sudoers", re.I), "Suspicious privilege activity", "Review sudo history, account privileges, and related authentication events."),
    ("HIGH", "web", re.compile(r"(?:union(?:%20|\s)+select|\.\./|/etc/passwd|<script|%3cscript|/\.env(?:\s|\?|$))", re.I), "Suspicious web probing detected", "Review the source address, requested endpoint, application logs, and edge/WAF controls."),
    ("LOW", "web", re.compile(r"/wp-login\.php(?:\s|\?|$)", re.I), "WordPress login endpoint requested", "Confirm whether WordPress is deployed and correlate repeated requests, source diversity, and HTTP response status before escalating."),
    ("MEDIUM", "network", re.compile(r"\bUFW BLOCK\b|\bfirewall\b.*\b(?:block|drop|deny)\b", re.I), "Firewall blocked inbound activity", "Review repeated sources and destination ports; confirm the traffic matches expected exposure."),
    ("MEDIUM", "service", re.compile(r"segfault|panic|fatal|crash|out of memory|oom-killer|service:\s+Failed|Failed with result", re.I), "Service or system failure", "Inspect surrounding events, resource pressure, and the affected service configuration."),
    ("MEDIUM", "error", re.compile(r"\berror\b|\bexception\b|\bdenied\b|\btimeout\b", re.I), "Operational error detected", "Inspect surrounding lines and the affected component for root cause."),
]

AUTH_FAILURE_RE = re.compile(r"failed password|authentication failure", re.I)
SOURCE_IP_PATTERNS = (
    re.compile(r"\bfrom\s+(?P<ip>[^\s,;]+)", re.I),
    re.compile(r"\brhost=(?P<ip>[^\s,;]+)", re.I),
    re.compile(r"\bsource(?:_ip| address| network address)?[=:]\s*(?P<ip>[^\s,;]+)", re.I),
    re.compile(r"\bsrc(?:_ip)?[=:]\s*(?P<ip>[^\s,;]+)", re.I),
)
ACCOUNT_PATTERNS = (
    re.compile(r"failed password for (?:invalid user )?(?P<account>[^\s]+)", re.I),
    re.compile(r"\b(?:user|account|username)[=:]\s*(?P<account>[^\s,;]+)", re.I),
)
HOST_PATTERNS = (
    re.compile(r"\bhost(?:name)?[=:]\s*(?P<host>[^\s,;]+)", re.I),
    re.compile(r"^\S+\s+(?P<host>[A-Za-z0-9._-]+)\s+(?:sshd|sudo|pam)", re.I),
)
TIMESTAMP_PATTERNS = (
    re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"),
    re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})"),
)


def redact(text: str) -> str:
    """Backward-compatible public redaction helper."""
    return redact_sensitive(text)


def _parse_timestamp(line: str) -> datetime | None:
    for pattern in TIMESTAMP_PATTERNS:
        match = pattern.search(line)
        if not match:
            continue
        value = match.group("ts").replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            continue
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def _valid_ip(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.strip("[](),;.")
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return None


def _first_match(patterns, line: str, group: str) -> str | None:
    for pattern in patterns:
        match = pattern.search(line)
        if match:
            return match.group(group).strip(".,;[]")
    return None


@dataclass(frozen=True)
class AuthEvent:
    timestamp: datetime | None
    source_ip: str | None
    account: str | None
    host: str | None
    evidence: str


def _auth_event(line: str) -> AuthEvent:
    return AuthEvent(
        _parse_timestamp(line),
        _valid_ip(_first_match(SOURCE_IP_PATTERNS, line, "ip")),
        _first_match(ACCOUNT_PATTERNS, line, "account"),
        _first_match(HOST_PATTERNS, line, "host"),
        line[:500],
    )


def _auth_finding(ip: str | None, count: int, event: AuthEvent, window_seconds: int) -> Finding:
    subject = ip or "an unparsed source"
    if count >= 20:
        severity, label = "CRITICAL", "Sustained authentication failures"
    elif count >= 5:
        severity, label = "HIGH", "Possible brute-force activity"
    else:
        severity, label = "MEDIUM", "Repeated authentication failures"
    qualifiers = []
    if event.account: qualifiers.append(f"account={event.account}")
    if event.host: qualifiers.append(f"host={event.host}")
    if event.timestamp: qualifiers.append(f"window={window_seconds}s")
    else: qualifiers.append("timestamp unavailable; correlated by bounded event order")
    return Finding(
        severity, "authentication", f"{label} from {subject}",
        f"{count} failures; " + "; ".join(qualifiers) + f"; latest={event.evidence}",
        "Correlate successful logons, target accounts, source ownership, MFA, and rate limiting before concluding malicious intent.",
    )


class AnalysisState:
    """Bounded cross-chunk correlation state used by file, stream, and live analysis."""
    def __init__(self, auth_window_seconds: int = 300, max_auth_events: int = 10_000):
        if auth_window_seconds < 1 or max_auth_events < 1:
            raise ValueError("correlation limits must be positive")
        self.auth_window_seconds = auth_window_seconds
        self.max_auth_events = max_auth_events
        self._auth: dict[str, deque[AuthEvent]] = defaultdict(deque)
        self._missing_ts: dict[str, deque[AuthEvent]] = defaultdict(deque)
        self._latest_ts: datetime | None = None
        self._other_findings: list[Finding] = []
        self.dropped_auth_events = 0

    def _add_auth(self, event: AuthEvent) -> None:
        key = event.source_ip or "<unknown>"
        if event.timestamp is None:
            bucket = self._missing_ts[key]
            bucket.append(event)
            while len(bucket) > min(self.max_auth_events, 20):
                bucket.popleft(); self.dropped_auth_events += 1
            return
        if self._latest_ts is None or event.timestamp > self._latest_ts:
            self._latest_ts = event.timestamp
        bucket = self._auth[key]
        bucket.append(event)
        cutoff = self._latest_ts.timestamp() - self.auth_window_seconds
        for events in self._auth.values():
            while events and events[0].timestamp and events[0].timestamp.timestamp() < cutoff:
                events.popleft()
        total = sum(len(events) for events in self._auth.values())
        while total > self.max_auth_events:
            oldest_key = min((k for k, v in self._auth.items() if v), key=lambda k: self._auth[k][0].timestamp)
            self._auth[oldest_key].popleft(); self.dropped_auth_events += 1; total -= 1

    def process(self, raw: str) -> None:
        line = redact(raw.strip())
        if not line: return
        windows_event = parse_windows_security_line(line)
        if windows_event is not None:
            signal = signal_for_event(windows_event)
            if windows_event.event_id == 4625:
                self._add_auth(AuthEvent(_parse_timestamp(windows_event.timestamp), _valid_ip(windows_event.source_ip), windows_event.account, windows_event.workstation, line[:500]))
                return
            if signal is not None:
                self._other_findings.append(Finding(signal.severity, signal.category, signal.title, signal.evidence, signal.recommendation)); return
        if AUTH_FAILURE_RE.search(line):
            self._add_auth(_auth_event(line)); return
        for severity, category, pattern, title, recommendation in RULES:
            if pattern.search(line):
                self._other_findings.append(Finding(severity, category, title, line[:500], recommendation)); break

    def findings(self) -> list[Finding]:
        findings = list(self._other_findings)
        correlated: list[Finding] = []
        for key, events in self._auth.items():
            if events: correlated.append(_auth_finding(None if key == "<unknown>" else key, len(events), events[-1], self.auth_window_seconds))
        for key, events in self._missing_ts.items():
            if events: correlated.append(_auth_finding(None if key == "<unknown>" else key, len(events), events[-1], self.auth_window_seconds))
        correlated.sort(key=lambda item: item.title)
        return correlated + findings


def analyze_lines(lines: list[str], auth_window_seconds: int = 300) -> list[Finding]:
    state = AnalysisState(auth_window_seconds=auth_window_seconds)
    for line in lines: state.process(line)
    return state.findings()


def analyze_file(path: Path, auth_window_seconds: int = 300) -> tuple[int, list[Finding]]:
    state = AnalysisState(auth_window_seconds=auth_window_seconds)
    count = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for count, line in enumerate(handle, 1): state.process(line)
    return count, state.findings()
