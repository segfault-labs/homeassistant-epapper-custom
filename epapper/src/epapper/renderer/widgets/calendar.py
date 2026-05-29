"""Calendar widget: today / tomorrow / next-day agenda with inverted now-event."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Callable

from epapper.ha_state import HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.fonts import font
from epapper.renderer.layout import Rect

CZECH_DAYS_SHORT = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
CZECH_MONTHS_GENITIVE = ["ledna", "února", "března", "dubna", "května", "června",
                        "července", "srpna", "září", "října", "listopadu", "prosince"]


@dataclass
class _Ev:
    summary: str
    start: datetime
    end: datetime
    location: str


def _truncate(text: str, max_px: int, f) -> str:
    if f.getlength(text) <= max_px:
        return text
    while text and f.getlength(text + "…") > max_px:
        text = text[:-1]
    return text + "…"


class CalendarWidget:
    def __init__(
        self,
        calendar_entity: str,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self._entity = calendar_entity
        self._now = now

    def watched_entities(self) -> list[str]:
        return [self._entity]

    def render(self, canvas: Canvas, region: Rect, state: HAState) -> None:
        draw = canvas.draw
        f_h = font("bold", 11)
        f_t = font("bold", 13)
        f_d = font("regular", 13)
        f_m = font("regular", 11)

        entity = state.get(self._entity)
        events = self._parse_events(entity.attributes.get("all_events", []) if entity else [])

        now = self._now()
        today = now.date()
        groups = self._group_by_day(events, today)

        y = region.y + 4
        for label, evs in groups:
            draw.text((region.x, y), label.upper(), font=f_h, fill=0)
            y += 16
            for ev in evs:
                if y + 22 > region.bottom:
                    break
                is_now = ev.start <= now < ev.end
                self._draw_event(draw, region, y, ev, f_t, f_d, f_m, is_now)
                y += 22
            y += 4
            if y >= region.bottom:
                break

    def _parse_events(self, raw_events: list[dict]) -> list[_Ev]:
        result = []
        for r in raw_events:
            try:
                start = datetime.fromisoformat(r["start"])
                end = datetime.fromisoformat(r["end"])
                result.append(_Ev(
                    summary=r.get("summary", ""),
                    start=start,
                    end=end,
                    location=r.get("location", "") or "",
                ))
            except (KeyError, ValueError):
                continue
        return sorted(result, key=lambda e: e.start)

    def _group_by_day(self, events: list[_Ev], today: date) -> list[tuple[str, list[_Ev]]]:
        groups: dict[date, list[_Ev]] = {}
        for ev in events:
            d = ev.start.date()
            if d < today:
                continue
            groups.setdefault(d, []).append(ev)

        labeled: list[tuple[str, list[_Ev]]] = []
        for d in sorted(groups):
            if d == today:
                label = "Agenda — dnes"
            elif d == today + timedelta(days=1):
                label = f"Zítra · {CZECH_DAYS_SHORT[d.weekday()].lower()}"
            else:
                label = f"{CZECH_DAYS_SHORT[d.weekday()]} · {d.day}. {CZECH_MONTHS_GENITIVE[d.month - 1]}"
            labeled.append((label, groups[d]))
        return labeled

    def _draw_event(self, draw, region, y, ev, f_t, f_d, f_m, is_now):
        time_txt = ev.start.strftime("%H:%M")
        title_x = region.x + 56
        max_title_px = region.right - title_x
        title = _truncate(ev.summary, max_title_px, f_d)

        if is_now:
            draw.rectangle((region.x - 2, y - 1, region.right + 2, y + 18), fill=0)
            draw.text((region.x, y + 2), time_txt, font=f_t, fill=1)
            draw.text((title_x, y + 2), title, font=f_d, fill=1)
            if ev.location:
                meta = f"— {ev.location}"
                meta = _truncate(meta, max_title_px - f_d.getlength(title) - 6, f_m)
                draw.text((title_x + f_d.getlength(title) + 6, y + 4), meta, font=f_m, fill=1)
        else:
            draw.text((region.x, y + 2), time_txt, font=f_t, fill=0)
            draw.text((title_x, y + 2), title, font=f_d, fill=0)
            if ev.location:
                meta = f"— {ev.location}"
                draw.text((title_x + f_d.getlength(title) + 6, y + 4), meta, font=f_m, fill=0)
        # dotted bottom
        for x in range(region.x, region.right, 3):
            draw.point((x, y + 20), fill=0)
