"""Vector weather icons drawn with PIL primitives.

The previous implementation used emoji glyphs (☀ ⛅ 🌧 …), but the bundled Inter
font has no emoji coverage, so they rendered as empty tofu boxes on the panel.
These icons are drawn from lines/ellipses/polygons instead — crisp in 1-bit and
font-independent.

`draw_weather_icon(draw, x, y, size, condition)` draws inside the square box with
top-left (x, y) and the given side length. Black = 0, white = 255 (mode "1").
"""
from __future__ import annotations

from PIL import ImageDraw

BLACK = 0
WHITE = 255


def _sun(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float) -> None:
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=BLACK, width=2)
    # 8 rays
    import math
    rr_in, rr_out = r + 2, r + 5
    for k in range(8):
        a = k * math.pi / 4
        draw.line(
            (cx + rr_in * math.cos(a), cy + rr_in * math.sin(a),
             cx + rr_out * math.cos(a), cy + rr_out * math.sin(a)),
            fill=BLACK, width=2,
        )


def _moon(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float) -> None:
    # Full black disk, then carve a white disk offset to the upper-right.
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BLACK)
    off = r * 0.6
    draw.ellipse((cx - r + off, cy - r - off * 0.4,
                  cx + r + off, cy + r - off * 0.4), fill=WHITE)


def _cloud(draw: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float,
           fill_white: bool = True) -> None:
    # A cloud built from three lobes + a flat base, outlined in black.
    if fill_white:
        draw.rectangle((x, y, x + w, y + h), fill=WHITE)
    base_y = y + h
    draw.ellipse((x, y + h * 0.35, x + w * 0.5, base_y), fill=WHITE, outline=BLACK, width=2)
    draw.ellipse((x + w * 0.2, y, x + w * 0.7, base_y), fill=WHITE, outline=BLACK, width=2)
    draw.ellipse((x + w * 0.45, y + h * 0.25, x + w, base_y), fill=WHITE, outline=BLACK, width=2)
    # flat-ish bottom to hide inner outline seams
    draw.rectangle((x + w * 0.12, y + h * 0.7, x + w * 0.88, base_y), fill=WHITE)
    draw.line((x + w * 0.12, base_y, x + w * 0.88, base_y), fill=BLACK, width=2)


def draw_weather_icon(draw: ImageDraw.ImageDraw, x: float, y: float,
                      size: float, condition: str) -> None:
    """Draw a weather icon for `condition` in the box at (x, y) of side `size`."""
    cx, cy = x + size / 2, y + size / 2

    if condition == "sunny":
        _sun(draw, cx, cy, size * 0.26)
        return
    if condition == "clear-night":
        _moon(draw, cx, cy, size * 0.32)
        return
    if condition == "partlycloudy":
        _sun(draw, x + size * 0.32, y + size * 0.32, size * 0.16)
        _cloud(draw, x + size * 0.18, y + size * 0.4, size * 0.72, size * 0.42)
        return
    if condition in ("cloudy", "fog"):
        _cloud(draw, x + size * 0.05, y + size * 0.22, size * 0.9, size * 0.5)
        if condition == "fog":
            for i in range(3):
                ly = y + size * (0.78 + i * 0.08)
                draw.line((x + size * 0.15, ly, x + size * 0.85, ly), fill=BLACK, width=2)
        return
    if condition in ("rainy", "snowy", "lightning"):
        _cloud(draw, x + size * 0.05, y + size * 0.12, size * 0.9, size * 0.46)
        below = y + size * 0.62
        if condition == "rainy":
            for i in range(3):
                rx = x + size * (0.28 + i * 0.22)
                draw.line((rx, below, rx - size * 0.08, below + size * 0.22),
                          fill=BLACK, width=2)
        elif condition == "snowy":
            for i in range(3):
                sx = x + size * (0.3 + i * 0.2)
                _snowflake(draw, sx, below + size * 0.12, size * 0.07)
        else:  # lightning
            bx = x + size * 0.45
            draw.line((bx, below, bx - size * 0.12, below + size * 0.18), fill=BLACK, width=2)
            draw.line((bx - size * 0.12, below + size * 0.18, bx + size * 0.04,
                       below + size * 0.18), fill=BLACK, width=2)
            draw.line((bx + size * 0.04, below + size * 0.18, bx - size * 0.08,
                       below + size * 0.4), fill=BLACK, width=2)
        return
    if condition == "windy":
        for i in range(3):
            ly = cy - size * 0.18 + i * size * 0.18
            draw.arc((x + size * 0.1, ly - size * 0.12, x + size * 0.75, ly + size * 0.12),
                     start=20, end=320, fill=BLACK, width=2)
        return

    # Unknown condition: a small filled marker so something shows.
    draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=BLACK)


def _snowflake(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float) -> None:
    import math
    for k in range(3):
        a = k * math.pi / 3
        draw.line((cx - r * math.cos(a), cy - r * math.sin(a),
                   cx + r * math.cos(a), cy + r * math.sin(a)), fill=BLACK, width=1)
