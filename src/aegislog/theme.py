from __future__ import annotations

from rich.text import Text

# AegisLog visual system: one controlled blue identity accent over cool neutral
# text. Semantic colors are deliberately reserved for real state and severity.
ACCENT = "#22D3EE"
ACCENT_SOFT = "#155E75"
ACCENT_BRIGHT = "#67E8F9"
CYAN = "#38BDF8"
BLUE = "#60A5FA"
VIOLET = "#C084FC"
MAGENTA = "#F472B6"
LIME = "#A3E635"
ORANGE = "#FB923C"
YELLOW = "#FACC15"
MUTED = "#94A3B8"
SUCCESS = "#34D399"
INFO = BLUE
WARNING = "#FBBF24"
HIGH = ORANGE
CRITICAL = "bold #FB7185"
INCIDENT = MAGENTA
ANOMALY = VIOLET
NEUTRAL = "#F8FAFC"
DIM = "#475569"
SURFACE = "#07111F"

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
