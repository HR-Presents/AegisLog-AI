from rich.console import Console

from aegislog.ui import compact_footer, console_title


def _render(renderable, width: int = 100) -> str:
    console = Console(record=True, force_terminal=False, color_system=None, width=width)
    console.print(renderable)
    return console.export_text(clear=False)


def test_console_title_has_product_page_and_status_hierarchy() -> None:
    output = _render(
        console_title(
            "System Health",
            subtitle="Inspect engine and collector readiness.",
            version="1.6.3",
        )
    )

    assert "AEGISLOG" in output
    assert "SYSTEM HEALTH" in output
    assert "v1.6.3" in output
    assert "READY" in output
    assert "LOCAL-FIRST" in output
    assert "READ-ONLY" in output
    assert "Inspect engine and collector readiness." in output
    assert "╭" not in output
    assert "╰" not in output


def test_compact_footer_is_low_chrome_guidance() -> None:
    output = _render(compact_footer("Press Enter to continue"))

    assert ">" in output
    assert "›" not in output
    assert "Press Enter to continue" in output
    assert "NEXT" not in output
