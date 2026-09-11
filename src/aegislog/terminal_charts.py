from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from .theme import ACCENT_BRIGHT, BLUE, CYAN, LIME, MAGENTA, MUTED, ORANGE, SUCCESS, VIOLET, WARNING

CHART_PALETTE = (MAGENTA, CYAN, LIME, ORANGE, VIOLET, BLUE, WARNING, SUCCESS, ACCENT_BRIGHT)


def horizontal_bar(value: float, maximum: float, width: int = 20, tone: str = CYAN) -> Text:
    filled = 0 if value <= 0 else max(1, round(value / max(maximum, 1.0) * width))
    bar = Text("█" * min(width, filled), style=tone)
    bar.append("░" * max(0, width - filled), style="#334155")
    return bar


def stacked_composition(values: Mapping[str, int], width: int = 38) -> RenderableType:
    items = [(label, count) for label, count in values.items() if count > 0]
    if not items:
        return Text("No composition data", style=MUTED)
    total = sum(count for _, count in items)
    remaining = width
    track = Text()
    legend = Text()
    for index, (label, count) in enumerate(items):
        segment = remaining if index == len(items) - 1 else max(1, round(count / total * width))
        segment = min(remaining, segment)
        tone = CHART_PALETTE[index % len(CHART_PALETTE)]
        track.append("█" * segment, style=tone)
        if index:
            legend.append("   ")
        legend.append(f"■ {label.upper()} {count / total:.0%}", style=tone)
        remaining -= segment
    return Group(track, legend)


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
    for y in range(-3, 4):
        row = Text()
        for x in range(-7, 8):
            radius = math.sqrt((x / 7.0) ** 2 + (y / 3.0) ** 2)
            if not 0.48 <= radius <= 1.08:
                row.append("  ")
                continue
            angle = (math.atan2(y / 3.0, x / 7.0) + math.pi) / (2 * math.pi)
            tone = stops[-1][1]
            for stop, candidate in stops:
                if angle <= stop:
                    tone = candidate
                    break
            row.append("██", style=tone)
        rows.append(row)
    center = Text(f"{total} total", style=f"bold {ACCENT_BRIGHT}", justify="center")
    legend = Table.grid(padding=(0, 1))
    legend.add_column()
    legend.add_column(justify="right")
    for index, (label, count) in enumerate(items[:6]):
        tone = CHART_PALETTE[index % len(CHART_PALETTE)]
        legend.add_row(Text(f"■ {label.upper()}", style=tone), Text(f"{count}  {count / total:.0%}", style=tone))
    layout = Table.grid(expand=True, padding=(0, 2))
    layout.add_column(width=31)
    layout.add_column(ratio=1)
    layout.add_row(Group(*rows, center), legend)
    return layout


def wave_chart(values: Sequence[float], *, width: int = 36, height: int = 7, tone: str = MAGENTA) -> RenderableType:
    if not values:
        return Text("No waveform data", style=MUTED)
    points: list[float] = []
    for column in range(width):
        position = column * (len(values) - 1) / max(1, width - 1)
        left = int(position)
        right = min(len(values) - 1, left + 1)
        fraction = position - left
        points.append(values[left] * (1 - fraction) + values[right] * fraction)
    low, high = min(points), max(points)
    span = max(high - low, 1.0)
    rows = [[" " for _ in range(width)] for _ in range(height)]
    previous: tuple[int, int] | None = None
    for x, value in enumerate(points):
        y = height - 1 - round((value - low) / span * (height - 1))
        rows[y][x] = "●"
        if previous is not None:
            px, py = previous
            if y < py:
                rows[min(py, height - 1)][x - 1] = "╱"
            elif y > py:
                rows[max(py, 0)][x - 1] = "╲"
            elif rows[y][x - 1] == " ":
                rows[y][x - 1] = "─"
        previous = (x, y)
    rendered = [Text(f"{high:>5.1f} │", style=MUTED)]
    for index, row in enumerate(rows):
        prefix = "      │" if index else ""
        rendered.append(Text(prefix).append("".join(row), style=tone))
    rendered.append(Text("  0.0 └" + "─" * width, style=MUTED))
    return Group(*rendered)


def vertical_histogram(items: Sequence[tuple[str, float]], *, height: int = 7) -> RenderableType:
    if not items:
        return Text("No histogram data", style=MUTED)
    maximum = max(value for _, value in items) or 1.0
    heights = [max(1, round(value / maximum * height)) if value else 0 for _, value in items]
    rows: list[Text] = []
    for level in range(height, 0, -1):
        row = Text(f"{maximum * level / height:>5.1f} │", style=MUTED)
        for index, bar_height in enumerate(heights):
            row.append("██" if bar_height >= level else "  ", style=CHART_PALETTE[index % len(CHART_PALETTE)])
            row.append(" ")
        rows.append(row)
    rows.append(Text("  0.0 └" + "───" * len(items), style=MUTED))
    rows.append(Text("       " + " ".join(label[-2:].rjust(2) for label, _ in items), style=MUTED))
    return Group(*rows)
