from __future__ import annotations

from rich.text import Text

# AegisLog SOC visual system: graphite terminal surfaces, cool cyan identity,
# warm neutral text, and semantic colors reserved for actual security state.
ACCENT = "#35C2C1"
ACCENT_SOFT = "#246B70"
MUTED = "#89959B"
SUCCESS = "#74B99A"
INFO = "#72A7B0"
WARNING = "#D5A85C"
HIGH = "#D87968"
CRITICAL = "bold #EF716C"
INCIDENT = "#C18A62"
ANOMALY = "#A28CB8"
NEUTRAL = "#D9E0DE"
DIM = "#59676B"
SURFACE = "#111718"

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
