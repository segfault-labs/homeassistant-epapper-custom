"""Todo widget: nákup + úkoly with fixed slots and +N overflow."""
from __future__ import annotations

from epapper.ha_state import HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.fonts import font
from epapper.renderer.layout import Rect

TODO_NAKUP_SLOTS = 3
TODO_UKOLY_SLOTS = 2
TODO_NAKUP_EXPANDED_SLOTS = 5
TODO_UKOLY_EXPANDED_SLOTS = 4


def _items(entity) -> list[str]:
    if entity is None:
        return []
    raw = entity.attribute("items", [])
    return [r["summary"] for r in raw if r.get("status") == "needs_action"]


def _truncate(text, max_px, f):
    if f.getlength(text) <= max_px:
        return text
    while text and f.getlength(text + "…") > max_px:
        text = text[:-1]
    return text + "…"


class TodoWidget:
    def __init__(self, nakup_entity: str, ukoly_entity: str) -> None:
        self._nakup = nakup_entity
        self._ukoly = ukoly_entity

    def watched_entities(self) -> list[str]:
        return [self._nakup, self._ukoly]

    def render(self, canvas: Canvas, region: Rect, state: HAState) -> None:
        draw = canvas.draw
        nakup = _items(state.get(self._nakup))
        ukoly = _items(state.get(self._ukoly))

        if not nakup and not ukoly:
            f = font("regular", 13)
            txt = "Žádné nákupy ani úkoly"
            tw = int(f.getlength(txt))
            draw.text((region.x + (region.w - tw) // 2, region.y + region.h // 2 - 8),
                      txt, font=f, fill=0)
            return

        if not nakup:
            self._draw_section(draw, region, region.y, "Úkoly", ukoly, TODO_UKOLY_EXPANDED_SLOTS)
            return
        if not ukoly:
            self._draw_section(draw, region, region.y, "Nákup", nakup, TODO_NAKUP_EXPANDED_SLOTS)
            return

        nakup_h = self._section_height(TODO_NAKUP_SLOTS, has_more=len(nakup) > TODO_NAKUP_SLOTS)
        self._draw_section(draw, region, region.y, "Nákup", nakup, TODO_NAKUP_SLOTS)
        self._draw_section(draw, region, region.y + nakup_h, "Úkoly", ukoly, TODO_UKOLY_SLOTS)

    def _section_height(self, slots: int, has_more: bool) -> int:
        return 16 + slots * 14 + (14 if has_more else 0)

    def _draw_section(self, draw, region, y, title, items, slots):
        f_h = font("bold", 11)
        f_count = font("regular", 10)
        f_row = font("regular", 12)
        f_more = font("regular", 11)

        total = len(items)
        visible = items[:slots]
        hidden = items[slots:]

        draw.text((region.x, y), title.upper(), font=f_h, fill=0)
        if total > slots:
            count_txt = f"{slots} z {total}"
            cw = int(f_count.getlength(count_txt))
            draw.text((region.right - cw, y + 1), count_txt, font=f_count, fill=0)
        y += 16

        for item in visible:
            txt = _truncate(item, region.w - 18, f_row)
            draw.rectangle((region.x, y + 2, region.x + 10, y + 12), outline=0, width=1)
            draw.text((region.x + 16, y), txt, font=f_row, fill=0)
            y += 14

        if hidden:
            sample = ", ".join(hidden[:2])
            if len(hidden) > 2:
                sample += ", …"
            more_txt = f"+ {len(hidden)} dalších ({sample})"
            more_txt = _truncate(more_txt, region.w - 16, f_more)
            draw.text((region.x + 16, y), more_txt, font=f_more, fill=0)
