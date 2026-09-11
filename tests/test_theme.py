from aegislog.theme import ACCENT, SECONDARY, SKY, risk_style, severity_style


def test_hybrid_palette_has_three_distinct_identity_accents():
    assert ACCENT == "#4FD1C5"
    assert SECONDARY == "#A78BFA"
    assert SKY == "#67B7FF"
    assert len({ACCENT, SECONDARY, SKY}) == 3


def test_severity_colors_keep_distinct_semantics():
    assert severity_style("CRITICAL") == "bold #FF6B72"
    assert severity_style("HIGH") == "#F08A7E"
    assert severity_style("MEDIUM") == "#F0C36A"
    assert severity_style("LOW") == "#67B7FF"
    assert severity_style("INFO") == "#AAB8BD"


def test_risk_colors_cover_clear_review_and_alert_states():
    assert risk_style("CLEAR") == "#78D6A3"
    assert risk_style("REVIEW") == "#F0C36A"
    assert risk_style("HIGH") == "#F08A7E"
    assert risk_style("CRITICAL") == "bold #FF6B72"
