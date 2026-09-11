from aegislog.theme import risk_style, severity_style


def test_severity_colors_keep_distinct_semantics():
    assert severity_style("CRITICAL") == "bold #EF747B"
    assert severity_style("HIGH") == "#D77A82"
    assert severity_style("MEDIUM") == "#D7AA63"
    assert severity_style("LOW") == "#7EA6D8"
    assert severity_style("INFO") == "#7D8797"


def test_risk_colors_cover_clear_review_and_alert_states():
    assert risk_style("CLEAR") == "#62B38F"
    assert risk_style("REVIEW") == "#D7AA63"
    assert risk_style("HIGH") == "#D77A82"
    assert risk_style("CRITICAL") == "bold #EF747B"
