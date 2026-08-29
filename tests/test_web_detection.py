from aegislog.engine import analyze_lines


def test_encoded_union_select_detection():
    findings = analyze_lines(['203.0.113.9 "GET /search?q=UNION%20SELECT HTTP/1.1" 403'])
    assert any(f.category == "web" for f in findings)


def test_path_traversal_detection():
    findings = analyze_lines(['203.0.113.9 "GET /../../etc/passwd HTTP/1.1" 400'])
    assert any(f.category == "web" for f in findings)
