"""Transit widget: 3 rows of nearest departures per line."""
from __future__ import annotations

from epapper.ha_state import HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.fonts import font
from epapper.renderer.layout import Rect


class TransitWidget:
    def __init__(self, transit_entities: list[str]) -> None:
        self._entities = transit_entities

    def watched_entities(self) -> list[str]:
        return list(self._entities)

    def render(self, canvas: Canvas, region: Rect, state: HAState) -> None:
        draw = canvas.draw
        f_h = font("bold", 11)
        f_line = font("bold", 11)
        f_dst = font("regular", 12)
        f_dep = font("bold", 12)

        draw.text((region.x, region.y + 4), "MHD — ODJEZDY", font=f_h, fill=0)
        y = region.y + 22
        row_h = 20

        for entity_id in self._entities[:3]:
            if y + row_h > region.bottom:
                break
            e = state.get(entity_id)
            if e is None:
                continue
            line = e.attribute("line", "?")
            dst = e.attribute("destination", "?")
            departures = e.attribute("departures", [])
            dep_txt = ", ".join(f"{d} min" if i == 0 else str(d)
                                for i, d in enumerate(departures[:3]))

            # line pill (inverted)
            pill_w = max(20, int(f_line.getlength(line)) + 8)
            draw.rectangle((region.x, y, region.x + pill_w, y + 14), fill=0)
            text_x = region.x + (pill_w - int(f_line.getlength(line))) // 2
            draw.text((text_x, y + 1), line, font=f_line, fill=1)

            draw.text((region.x + pill_w + 6, y + 1), dst, font=f_dst, fill=0)

            # right-aligned departures
            dep_w = int(f_dep.getlength(dep_txt))
            draw.text((region.right - dep_w, y + 1), dep_txt, font=f_dep, fill=0)

            # dotted underline
            for x in range(region.x, region.right, 3):
                draw.point((x, y + 17), fill=0)
            y += row_h
