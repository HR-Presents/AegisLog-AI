from __future__ import annotations

from rich.text import Text

# AegisLog visual system: midnight surfaces, cool steel text and one controlled
# blue identity accent. Semantic colors are reserved for actual system state.
ACCENT = "#4C8DFF"
ACCENT_SOFT = "#315A9E"
MUTED = "#718096"
SUCCESS = "#4FAE86"
INFO = "#78A6D8"
WARNING = "#D6A85F"
HIGH = "#D96B72"
CRITICAL = "bold #F07178"
INCIDENT = "#8FA7C7"
ANOMALY = "#7F91AA"
NEUTRAL = "#E7EDF6"
DIM = "#46556B"
SURFACE = "#101722"

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
