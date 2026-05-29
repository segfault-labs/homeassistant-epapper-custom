"""Static layout regions on the 800x480 canvas. Coordinates are pixels.

Layout grid (after 8px outer padding):
  header   8..792 ×  8..40    (32 px tall full-width)
  calendar 8..488 × 48..328   (left, agenda)
  weather  496..792 × 48..200 (right top)
  transit  496..792 × 208..328 (right middle)
  todo     8..488 × 336..472  (left bottom)
  sensors  496..792 × 336..472 (right bottom)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)


LAYOUT: dict[str, Rect] = {
    "header":   Rect(x=8,   y=8,   w=784, h=32),
    "calendar": Rect(x=8,   y=48,  w=480, h=280),
    "weather":  Rect(x=496, y=48,  w=296, h=152),
    "transit":  Rect(x=496, y=208, w=296, h=120),
    "todo":     Rect(x=8,   y=336, w=480, h=136),
    "sensors":  Rect(x=496, y=336, w=296, h=136),
}
