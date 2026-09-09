from __future__ import annotations

from rich.text import Text

# AegisLog terminal palette. Structural UI stays quiet; semantic colors are
# reserved for state and severity so operators can scan screens quickly.
ACCENT = "bright_cyan"
ACCENT_SOFT = "cyan"
MUTED = "grey62"
SUCCESS = "green"
INFO = "bright_blue"
WARNING = "yellow"
HIGH = "red"
CRITICAL = "bold bright_red"
INCIDENT = "bright_cyan"
ANOMALY = "bright_blue"
NEUTRAL = "white"

SEVERITY_STYLES = {
    "CRITICAL": CRITICAL,
    "HIGH": HIGH,
    "MEDIUM": WARNING,
    "LOW": INFO,
    "INFO": MUTED,
}

RISK_STYLES = {
    "CRITICAL": CRITICAL,
    "HIGH": HIGH,
    "REVIEW": WARNING,
    "CLEAR": SUCCESS,
}


def severity_style(value: str) -> str:
    return SEVERITY_STYLES.get(value.upper(), NEUTRAL)


def risk_style(value: str) -> str:
    return RISK_STYLES.get(value.upper(), NEUTRAL)


def severity_text(value: str) -> Text:
    return Text(value, style=severity_style(value))


def risk_text(value: str) -> Text:
    return Text(value, style=f"bold {risk_style(value)}")
