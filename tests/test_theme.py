from aegislog.theme import risk_style, severity_style


def test_severity_colors_keep_distinct_semantics():
    assert severity_style("CRITICAL") == "bold #ff6b6b"
    assert severity_style("HIGH") == "#d96767"
    assert severity_style("MEDIUM") == "#d4a72c"
    assert severity_style("LOW") == "#6f93b5"
    assert severity_style("INFO") == "#8b949e"


def test_risk_colors_cover_clear_review_and_alert_states():
    assert risk_style("CLEAR") == "#56a36c"
    assert risk_style("REVIEW") == "#d4a72c"
    assert risk_style("HIGH") == "#d96767"
    assert risk_style("CRITICAL") == "bold #ff6b6b"
