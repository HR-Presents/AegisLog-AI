from aegislog.sanitize import terminal_safe


def test_removes_ansi_escape_sequence():
    assert terminal_safe("safe\x1b[31mred\x1b[0m") == "safered"


def test_removes_control_character():
    assert terminal_safe("hello\x00world") == "helloworld"
