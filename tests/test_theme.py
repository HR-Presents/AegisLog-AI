from aegislog.theme import risk_style, severity_style


def test_severity_colors_keep_distinct_semantics():
    assert severity_style("CRITICAL") == "bold bright_red"
    assert severity_style("HIGH") == "bright_red"
    assert severity_style("MEDIUM") == "yellow"
    assert severity_style("LOW") == "bright_blue"
    assert severity_style("INFO") == "cyan"


def test_risk_colors_cover_clear_review_and_alert_states():
    assert risk_style("CLEAR") == "bright_green"
    assert risk_style("REVIEW") == "yellow"
    assert risk_style("HIGH") == "bright_red"
    assert risk_style("CRITICAL") == "bold bright_red"
