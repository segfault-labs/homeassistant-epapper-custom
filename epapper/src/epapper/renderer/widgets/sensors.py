"""Sensors widget: 2x2 grid of value boxes."""
from __future__ import annotations

from dataclasses import dataclass, field

from epapper.ha_state import HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.fonts import font
from epapper.renderer.layout import Rect


@dataclass
class SensorSpec:
    title: str
    value_entity: str
    value_format: str = "{}"
    value_unit: str = ""
    subtitle: str = ""
    subtitle_entity: str | None = None
    subtitle_format: str = "{}"


class SensorsWidget:
    def __init__(self, specs: list[SensorSpec]) -> None:
        assert len(specs) <= 4, "sensors widget supports at most 4 boxes"
        self._specs = specs

    def watched_entities(self) -> list[str]:
        watched: list[str] = []
        for s in self._specs:
            watched.append(s.value_entity)
            if s.subtitle_entity:
                watched.append(s.subtitle_entity)
        return watched

    def render(self, canvas: Canvas, region: Rect, state: HAState) -> None:
        draw = canvas.draw
        f_label = font("regular", 9)
        f_value = font("bold", 22)
        f_unit = font("regular", 11)

        cols, rows = 2, 2
        box_w = (region.w - 6) // cols
        box_h = (region.h - 6) // rows
        for i, spec in enumerate(self._specs):
            cx = i % cols
            cy = i // cols
            bx = region.x + cx * (box_w + 6)
            by = region.y + cy * (box_h + 6)
            self._draw_box(draw, bx, by, box_w, box_h, spec, state,
                           f_label, f_value, f_unit)

    def _draw_box(self, draw, x, y, w, h, spec, state, f_label, f_value, f_unit):
        draw.rectangle((x, y, x + w, y + h), outline=0)
        draw.text((x + 4, y + 3), spec.title, font=f_label, fill=0)

        entity = state.get(spec.value_entity)
        if entity is None:
            value_txt = "—"
            unit_txt = ""
        else:
            try:
                fval = float(entity.state)
                value_txt = spec.value_format.format(fval)
            except (ValueError, TypeError):
                value_txt = entity.state
            unit_txt = spec.value_unit

        vx = x + (w - int(f_value.getlength(value_txt) + f_unit.getlength(unit_txt))) // 2
        draw.text((vx, y + 18), value_txt, font=f_value, fill=0)
        draw.text((vx + int(f_value.getlength(value_txt)) + 2, y + 30),
                  unit_txt, font=f_unit, fill=0)

        sub_txt = spec.subtitle
        if spec.subtitle_entity:
            sub_entity = state.get(spec.subtitle_entity)
            if sub_entity is not None:
                try:
                    sub_txt = spec.subtitle_format.format(float(sub_entity.state))
                except (ValueError, TypeError):
                    sub_txt = sub_entity.state
        sw = int(f_label.getlength(sub_txt))
        draw.text((x + (w - sw) // 2, y + h - 14), sub_txt, font=f_label, fill=0)
