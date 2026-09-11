from __future__ import annotations

from rich.text import Text

# AegisLog hybrid SOC visual system: luminous cyan/mint identity over a
# medium-contrast terminal canvas. Semantic colors remain reserved for state.
ACCENT = "#4FD1C5"
ACCENT_SOFT = "#5F7F83"
MUTED = "#AAB8BD"
SUCCESS = "#78D6A3"
INFO = "#8EC5D6"
WARNING = "#F0C36A"
HIGH = "#F08A7E"
CRITICAL = "bold #FF6B72"
INCIDENT = "#C8A7E8"
ANOMALY = "#9FB7E9"
NEUTRAL = "#F2F5F4"
DIM = "#728388"
SURFACE = "#263236"

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
