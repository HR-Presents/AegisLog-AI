from __future__ import annotations

from rich.text import Text

# AegisLog visual system: one controlled blue identity accent over cool neutral
# text. Semantic colors are deliberately reserved for real state and severity.
ACCENT = "#5B8CFF"
ACCENT_SOFT = "#385784"
ACCENT_BRIGHT = "#78A5FF"
CYAN = "#63C5DA"
VIOLET = "#9B8AFB"
MUTED = "#8391A6"
SUCCESS = "#62B38F"
INFO = "#8BA8C7"
WARNING = "#D2A65A"
HIGH = "#D56C73"
CRITICAL = "bold #EF747B"
INCIDENT = "#A0AEC0"
ANOMALY = "#91A0B5"
NEUTRAL = "#E8EDF5"
DIM = "#526177"
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
