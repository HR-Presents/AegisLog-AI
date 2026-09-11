from aegislog.theme import risk_style, severity_style


def test_severity_colors_keep_distinct_semantics():
    assert severity_style("CRITICAL") == "bold #FB7185"
    assert severity_style("HIGH") == "#FB923C"
    assert severity_style("MEDIUM") == "#FBBF24"
    assert severity_style("LOW") == "#60A5FA"
    assert severity_style("INFO") == "#94A3B8"


def test_risk_colors_cover_clear_review_and_alert_states():
    assert risk_style("CLEAR") == "#34D399"
    assert risk_style("REVIEW") == "#FBBF24"
    assert risk_style("HIGH") == "#FB923C"
    assert risk_style("CRITICAL") == "bold #FB7185"
