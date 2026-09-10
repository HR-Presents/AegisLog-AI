from aegislog.theme import risk_style, severity_style


def test_severity_colors_keep_distinct_semantics():
    assert severity_style("CRITICAL") == "bold #F07178"
    assert severity_style("HIGH") == "#D96B72"
    assert severity_style("MEDIUM") == "#D6A85F"
    assert severity_style("LOW") == "#78A6D8"
    assert severity_style("INFO") == "#8290A3"


def test_risk_colors_cover_clear_review_and_alert_states():
    assert risk_style("CLEAR") == "#4FAE86"
    assert risk_style("REVIEW") == "#D6A85F"
    assert risk_style("HIGH") == "#D96B72"
    assert risk_style("CRITICAL") == "bold #F07178"
