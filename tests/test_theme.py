from aegislog.theme import risk_style, severity_style


def test_severity_colors_keep_distinct_semantics():
    assert severity_style("CRITICAL") == "bold #EF747B"
    assert severity_style("HIGH") == "#D56C73"
    assert severity_style("MEDIUM") == "#D2A65A"
    assert severity_style("LOW") == "#8BA8C7"
    assert severity_style("INFO") == "#8391A6"


def test_risk_colors_cover_clear_review_and_alert_states():
    assert risk_style("CLEAR") == "#62B38F"
    assert risk_style("REVIEW") == "#D2A65A"
    assert risk_style("HIGH") == "#D56C73"
    assert risk_style("CRITICAL") == "bold #EF747B"
