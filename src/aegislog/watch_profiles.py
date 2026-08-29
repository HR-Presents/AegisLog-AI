from __future__ import annotations

from dataclasses import dataclass

from .engine import Finding
from .parsers import Event


@dataclass(frozen=True)
class WatchProfile:
    key: str
    label: str
    description: str
    keywords: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    services: tuple[str, ...] = ()
    trend_metrics: tuple[str, ...] = ()

    @property
    def is_all(self) -> bool:
        return self.key == "all"


_PROFILES: dict[str, WatchProfile] = {
    "all": WatchProfile(
        "all",
        "All activity",
        "Show the full defensive live view without profile filtering.",
        trend_metrics=("Failed logins", "Errors", "Firewall blocks"),
    ),
    "security": WatchProfile(
        "security",
        "Security",
        "Prioritize authentication, attack, firewall, privilege and suspicious activity.",
        keywords=(
            "attack", "brute", "credential", "failed password", "authentication failure",
            "invalid user", "firewall", "blocked", "denied", "suspicious", "exploit",
            "powershell", "privilege", "sudo", "malware", "scan", "injection", "traversal",
        ),
        categories=("auth", "security", "attack", "firewall", "privilege", "web"),
        trend_metrics=("Failed logins", "Firewall blocks", "Errors"),
    ),
    "authentication": WatchProfile(
        "authentication",
        "Authentication",
        "Focus on login failures, account activity and credential-related signals.",
        keywords=(
            "login", "logon", "auth", "password", "credential", "invalid user", "account",
            "sshd", "pam", "failed", "success", "sudo",
        ),
        categories=("auth", "credential", "account"),
        services=("sshd", "ssh", "pam", "winlogon"),
        trend_metrics=("Failed logins",),
    ),
    "web": WatchProfile(
        "web",
        "Web",
        "Focus on HTTP services, probes, application errors and public-facing attack signals.",
        keywords=(
            "http", "https", "nginx", "apache", "request", "status=", "404", "500",
            "sql", "injection", "traversal", "/.env", "/etc/passwd", "user-agent", "uri",
        ),
        categories=("web", "http", "application"),
        services=("nginx", "apache", "httpd", "iis"),
        trend_metrics=("Errors",),
    ),
    "docker": WatchProfile(
        "docker",
        "Docker",
        "Focus on container runtime, Docker service and containerized application activity.",
        keywords=("docker", "container", "containerd", "dockerd", "image", "compose", "kubernetes", "kube"),
        categories=("docker", "container"),
        services=("docker", "dockerd", "containerd"),
        trend_metrics=("Errors", "Firewall blocks"),
    ),
    "operations": WatchProfile(
        "operations",
        "Operations",
        "Focus on errors, timeouts, service failures and operational health signals.",
        keywords=(
            "error", "exception", "timeout", "failed", "failure", "unavailable", "down",
            "restart", "crash", "oom", "memory", "disk", "database", "systemd", "service",
        ),
        categories=("system", "service", "database", "operations", "availability"),
        trend_metrics=("Errors",),
    ),
}


def profile_choices() -> tuple[str, ...]:
    return tuple(_PROFILES)


def get_profile(name: str | None) -> WatchProfile:
    key = (name or "all").strip().lower()
    try:
        return _PROFILES[key]
    except KeyError as exc:
        allowed = ", ".join(profile_choices())
        raise ValueError(f"Unknown watch profile '{name}'. Choose one of: {allowed}") from exc


def _haystack(*values: str | None) -> str:
    return " ".join(value or "" for value in values).lower()


def finding_matches(profile: WatchProfile, finding: Finding) -> bool:
    if profile.is_all:
        return True
    text = _haystack(finding.category, finding.title, finding.evidence)
    return any(token in text for token in (*profile.categories, *profile.keywords))


def event_matches(profile: WatchProfile, event: Event) -> bool:
    if profile.is_all:
        return True
    text = _haystack(event.service, event.level, event.message)
    return any(token in text for token in (*profile.services, *profile.keywords))


def filter_findings(profile: WatchProfile, findings: list[Finding]) -> list[Finding]:
    return [item for item in findings if finding_matches(profile, item)]


def filter_events(profile: WatchProfile, events: list[Event]) -> list[Event]:
    return [item for item in events if event_matches(profile, item)]
