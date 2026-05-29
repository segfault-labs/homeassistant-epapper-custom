"""Widget Protocol — anything that can render into a region of the canvas."""
from __future__ import annotations

from typing import Protocol

from epapper.ha_state import HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.layout import Rect


class Widget(Protocol):
    def watched_entities(self) -> list[str]:
        """Entity IDs whose state_changed should trigger a re-render."""
        ...

    def render(self, canvas: Canvas, region: Rect, state: HAState) -> None:
        """Draw widget contents into the given region. Must not draw outside region."""
        ...
