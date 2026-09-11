from __future__ import annotations

import math
import os
import sys
from collections.abc import Mapping, Sequence

from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from .theme import ACCENT_BRIGHT, BLUE, CYAN, DIM, LIME, MAGENTA, MUTED, ORANGE, SUCCESS, VIOLET, WARNING

CHART_PALETTE = (MAGENTA, CYAN, LIME, ORANGE, VIOLET, BLUE, WARNING, SUCCESS, ACCENT_BRIGHT)
_BRAILLE_BITS = ((0x01, 0x08), (0x02, 0x10), (0x04, 0x20), (0x40, 0x80))
_BLOCKS = " ▁▂▃▄▅▆▇█"


def unicode_charts_supported() -> bool:
    """Return whether high-resolution chart glyphs are safe on this terminal."""
    forced = os.getenv("AEGISLOG_ASCII_CHARTS", "").strip().lower()
    if forced in {"1", "true", "yes", "on"}:
        return False
    if forced in {"0", "false", "no", "off"}:
        return True
    if os.getenv("WT_SESSION") or os.getenv("TERM_PROGRAM") in {"Windows_Terminal", "WezTerm", "iTerm.app"}:
        return True
    encoding = (getattr(sys.stdout, "encoding", None) or "").lower().replace("-", "")
    return "utf8" in encoding or sys.platform != "win32"


def _glyph(modern: str, fallback: str) -> str:
    return modern if unicode_charts_supported() else fallback


def horizontal_bar(value: float, maximum: float, width: int = 20, tone: str = CYAN) -> Text:
    ratio = max(0.0, min(1.0, value / max(maximum, 1.0)))
    if not unicode_charts_supported():
        filled = 0 if value <= 0 else max(1, round(ratio * width))
        return Text("#" * min(width, filled), style=tone).append("." * max(0, width - filled), style=DIM)
    units = round(ratio * width * 8)
    full, fraction = divmod(units, 8)
    bar = Text("█" * min(width, full), style=tone)
    if full < width and fraction:
        bar.append(_BLOCKS[fraction], style=tone)
        full += 1
    bar.append("·" * max(0, width - full), style=DIM)
    return bar


def stacked_composition(values: Mapping[str, int], width: int = 38) -> RenderableType:
    items = [(label, count) for label, count in values.items() if count > 0]
    if not items:
        return Text("No composition data", style=MUTED)
    total = sum(count for _, count in items)
    remaining = width
    track = Text()
    legend = Text()
    fill, marker = _glyph("█", "#"), _glyph("■", "#")
    for index, (label, count) in enumerate(items):
        segment = remaining if index == len(items) - 1 else max(1, round(count / total * width))
        segment = min(remaining, segment)
        tone = CHART_PALETTE[index % len(CHART_PALETTE)]
        track.append(fill * segment, style=tone)
        if index:
            legend.append("   ")
        legend.append(f"{marker} {label.upper()} {count / total:.0%}", style=tone)
        remaining -= segment
    return Group(track, legend)


def _braille_character(points: set[tuple[int, int]]) -> str:
    bits = 0
    for x, y in points:
        bits |= _BRAILLE_BITS[y][x]
    return chr(0x2800 + bits) if bits else " "


def _tone_for_angle(angle: float, stops: Sequence[tuple[float, str]]) -> str:
    return next((candidate for stop, candidate in stops if angle <= stop), stops[-1][1])


def donut_chart(values: Mapping[str, int]) -> RenderableType:
    items = [(label, count) for label, count in values.items() if count > 0]
    if not items:
        return Text("No distribution data", style=MUTED)
    total = sum(count for _, count in items)
    stops: list[tuple[float, str]] = []
    running = 0.0
    for index, (_, count) in enumerate(items):
        running += count / total
        stops.append((running, CHART_PALETTE[index % len(CHART_PALETTE)]))

    rows: list[Text] = []
    if unicode_charts_supported():
        char_width, char_height = 18, 7
        pixel_width, pixel_height = char_width * 2, char_height * 4
        cx, cy = (pixel_width - 1) / 2, (pixel_height - 1) / 2
        for char_y in range(char_height):
            row = Text()
            for char_x in range(char_width):
                points: set[tuple[int, int]] = set()
                angles: list[float] = []
                for dot_y in range(4):
                    for dot_x in range(2):
                        px, py = char_x * 2 + dot_x, char_y * 4 + dot_y
                        dx, dy = (px - cx) / (pixel_width * 0.48), (py - cy) / (pixel_height * 0.48)
                        radius = math.hypot(dx, dy)
                        if 0.55 <= radius <= 1.0:
                            points.add((dot_x, dot_y))
                            angles.append((math.atan2(dy, dx) + math.pi) / (2 * math.pi))
                if not points:
                    row.append(" ")
                    continue
                row.append(_braille_character(points), style=f"bold {_tone_for_angle(sum(angles) / len(angles), stops)}")
            rows.append(row)
    else:
        for y in range(-3, 4):
            row = Text()
            for x in range(-7, 8):
                radius = math.sqrt((x / 7.0) ** 2 + (y / 3.0) ** 2)
                if not 0.48 <= radius <= 1.08:
                    row.append("  ")
                    continue
                angle = (math.atan2(y / 3.0, x / 7.0) + math.pi) / (2 * math.pi)
                row.append("##", style=_tone_for_angle(angle, stops))
            rows.append(row)

    center = Text(f"{total} total", style=f"bold {ACCENT_BRIGHT}", justify="center")
    legend = Table.grid(padding=(0, 1))
    legend.add_column()
    legend.add_column(justify="right")
    marker = _glyph("●", "#")
    for index, (label, count) in enumerate(items[:6]):
        tone = CHART_PALETTE[index % len(CHART_PALETTE)]
        legend.add_row(Text(f"{marker} {label.upper()}", style=tone), Text(f"{count}  {count / total:.0%}", style=tone))
    layout = Table.grid(expand=True, padding=(0, 2))
    layout.add_column(width=31)
    layout.add_column(ratio=1)
    layout.add_row(Group(*rows, center), legend)
    return layout


def _sample(values: Sequence[float], size: int) -> list[float]:
    if len(values) == 1:
        return [float(values[0])] * size
    sampled: list[float] = []
    for column in range(size):
        position = column * (len(values) - 1) / max(1, size - 1)
        left = int(position)
        right = min(len(values) - 1, left + 1)
        fraction = position - left
        sampled.append(values[left] * (1 - fraction) + values[right] * fraction)
    return sampled


def _braille_plot(values: Sequence[float], width: int, height: int, *, fill: bool) -> list[str]:
    pixel_width, pixel_height = width * 2, height * 4
    sampled = _sample(values, pixel_width)
    low, high = min(sampled), max(sampled)
    span = max(high - low, 1.0)
    pixels: set[tuple[int, int]] = set()
    previous_y: int | None = None
    for x, value in enumerate(sampled):
        y = pixel_height - 1 - round((value - low) / span * (pixel_height - 1))
        if previous_y is not None:
            for between in range(min(previous_y, y), max(previous_y, y) + 1):
                pixels.add((x, between))
        pixels.add((x, y))
        if fill:
            for below in range(y + 2, pixel_height, 3):
                pixels.add((x, below))
        previous_y = y
    rows: list[str] = []
    for char_y in range(height):
        line = []
        for char_x in range(width):
            local = {(dx, dy) for dy in range(4) for dx in range(2) if (char_x * 2 + dx, char_y * 4 + dy) in pixels}
            line.append(_braille_character(local))
        rows.append("".join(line))
    return rows


def wave_chart(values: Sequence[float], *, width: int = 36, height: int = 7, tone: str = MAGENTA, fill: bool = True) -> RenderableType:
    if not values:
        return Text("No waveform data", style=MUTED)
    high = max(values)
    if unicode_charts_supported():
        rows = _braille_plot(values, width, height, fill=fill)
        rendered = [Text(f"{high:>5.1f} │", style=MUTED).append(rows[0], style=f"bold {tone}")]
        rendered.extend(Text("      │", style=MUTED).append(row, style=tone) for row in rows[1:])
        rendered.append(Text("  0.0 └" + "─" * width, style=MUTED))
        return Group(*rendered)

    points = _sample(values, width)
    low, maximum = min(points), max(points)
    span = max(maximum - low, 1.0)
    rows = [[" " for _ in range(width)] for _ in range(height)]
    previous_y: int | None = None
    for x, value in enumerate(points):
        y = height - 1 - round((value - low) / span * (height - 1))
        rows[y][x] = "*"
        if previous_y is not None:
            rows[previous_y][x - 1] = "/" if y < previous_y else "\\" if y > previous_y else "-"
        previous_y = y
    rendered = [Text(f"{maximum:>5.1f} |", style=MUTED)]
    for index, row in enumerate(rows):
        rendered.append(Text("      |" if index else "").append("".join(row), style=tone))
    rendered.append(Text("  0.0 +" + "-" * width, style=MUTED))
    return Group(*rendered)


def vertical_histogram(items: Sequence[tuple[str, float]], *, height: int = 7, width: int = 38) -> RenderableType:
    if not items:
        return Text("No histogram data", style=MUTED)
    maximum = max(value for _, value in items) or 1.0
    gap = 1
    bar_width = max(2, min(7, (width - gap * (len(items) - 1)) // len(items)))
    rows: list[Text] = []
    for level in range(height, 0, -1):
        row = Text(f"{maximum * level / height:>5.1f} {_glyph('│', '|')}", style=MUTED)
        for index, (_, value) in enumerate(items):
            units = value / maximum * height
            partial = max(0, min(7, round((units - level + 1) * 8)))
            cell = _glyph("█", "#") if units >= level else _glyph(_BLOCKS[partial], " ") if units > level - 1 else " "
            row.append(cell * bar_width, style=CHART_PALETTE[index % len(CHART_PALETTE)])
            if index < len(items) - 1:
                row.append(" " * gap)
        rows.append(row)
    axis_width = bar_width * len(items) + gap * (len(items) - 1)
    rows.append(Text(f"  0.0 {_glyph('└', '+')}" + _glyph("─", "-") * axis_width, style=MUTED))
    labels = [(label[-5:] if ":" in label else label[-bar_width:]).center(bar_width) for label, _ in items]
    rows.append(Text(" " * 7 + " ".join(labels), style=MUTED))
    return Group(*rows)


def sparkline(values: Sequence[float], *, width: int = 18, tone: str = CYAN) -> Text:
    if not values:
        return Text(_glyph("·", ".") * width, style=DIM)
    points = _sample(values, width)
    low, high = min(points), max(points)
    span = max(high - low, 1.0)
    if unicode_charts_supported():
        return Text("".join(_BLOCKS[1 + round((value - low) / span * 7)] for value in points), style=tone)
    levels = ".:-=+*#%@"
    return Text("".join(levels[round((value - low) / span * (len(levels) - 1))] for value in points), style=tone)


def radar_chart(values: Mapping[str, float], *, width: int = 31, height: int = 11, tone: str = ORANGE) -> RenderableType:
    items = [(label, max(0.0, float(value))) for label, value in values.items()]
    if len(items) < 3:
        return Text("Not enough dimensions for a radar profile", style=MUTED)
    maximum = max((value for _, value in items), default=0.0) or 1.0
    if not unicode_charts_supported():
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(ratio=1)
        table.add_column(width=14)
        table.add_column(width=7, justify="right")
        for index, (label, value) in enumerate(items):
            item_tone = CHART_PALETTE[index % len(CHART_PALETTE)]
            table.add_row(label.upper(), horizontal_bar(value, maximum, 14, item_tone), f"{value:.0f}")
        return table

    pixel_width, pixel_height = width * 2, height * 4
    cx, cy = (pixel_width - 1) / 2, (pixel_height - 1) / 2
    rx, ry = pixel_width * 0.43, pixel_height * 0.40
    pixels: set[tuple[int, int]] = set()

    def add_line(a: tuple[float, float], b: tuple[float, float], steps: int = 120) -> None:
        for step in range(steps + 1):
            fraction = step / steps
            pixels.add((round(a[0] + (b[0] - a[0]) * fraction), round(a[1] + (b[1] - a[1]) * fraction)))

    outer: list[tuple[float, float]] = []
    data: list[tuple[float, float]] = []
    for index, (_, value) in enumerate(items):
        angle = -math.pi / 2 + index * 2 * math.pi / len(items)
        outer.append((cx + math.cos(angle) * rx, cy + math.sin(angle) * ry))
        ratio = 0.12 + 0.88 * value / maximum
        data.append((cx + math.cos(angle) * rx * ratio, cy + math.sin(angle) * ry * ratio))
    for index, point in enumerate(outer):
        add_line((cx, cy), point, 60)
        add_line(point, outer[(index + 1) % len(outer)], 80)
        add_line(data[index], data[(index + 1) % len(data)], 80)

    rows: list[Text] = []
    for char_y in range(height):
        row = Text()
        for char_x in range(width):
            local = {(dx, dy) for dy in range(4) for dx in range(2) if (char_x * 2 + dx, char_y * 4 + dy) in pixels}
            row.append(_braille_character(local), style=tone if local else DIM)
        rows.append(row)
    legend = Text()
    for index, (label, value) in enumerate(items):
        if index:
            legend.append("  ")
        legend.append(f"{label.upper()} {value:.0f}", style=CHART_PALETTE[index % len(CHART_PALETTE)])
    return Group(*rows, legend)
