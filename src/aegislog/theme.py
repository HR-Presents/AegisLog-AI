from __future__ import annotations

from rich.text import Text

# Restrained terminal palette. Navigation stays neutral; color is reserved for
# selection, state, and security severity so it carries meaning instead of
# becoming decoration.
ACCENT = "#5fb3a6"
ACCENT_SOFT = "#3f7f78"
MUTED = "#8b949e"
SUCCESS = "#56a36c"
INFO = "#6f93b5"
WARNING = "#d4a72c"
HIGH = "#d96767"
CRITICAL = "bold #ff6b6b"
INCIDENT = "#8fa6c9"
ANOMALY = "#8497b0"
NEUTRAL = "#e6edf3"

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
