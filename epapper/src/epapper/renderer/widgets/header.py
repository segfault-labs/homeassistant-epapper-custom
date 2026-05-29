"""Header bar: date on the left, weather + refresh-time + battery on the right."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from epapper.ha_state import HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.fonts import font
from epapper.renderer.layout import Rect

CZECH_DAYS = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
CZECH_MONTHS = ["ledna", "února", "března", "dubna", "května", "června",
                "července", "srpna", "září", "října", "listopadu", "prosince"]

WEATHER_ICON = {
    "sunny": "☀", "clear-night": "☾", "cloudy": "☁", "partlycloudy": "⛅",
    "rainy": "🌧", "snowy": "❄", "fog": "≡", "windy": "⤳",
}


class HeaderWidget:
    def __init__(
        self,
        weather_entity: str,
        battery_entity: str,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self._weather_entity = weather_entity
        self._battery_entity = battery_entity
        self._now = now

    def watched_entities(self) -> list[str]:
        return [self._weather_entity, self._battery_entity]

    def render(self, canvas: Canvas, region: Rect, state: HAState) -> None:
        draw = canvas.draw
        f_bold = font("bold", 14)
        f_reg = font("regular", 11)

        # left: "Pátek 17. května · týden 20"
        now = self._now()
        weekday = CZECH_DAYS[now.weekday()]
        month = CZECH_MONTHS[now.month - 1]
        iso_week = now.isocalendar().week
        left = f"{weekday} {now.day}. {month} · týden {iso_week}"
        draw.text((region.x, region.y + 8), left, font=f_bold, fill=0)

        # right cluster, right-aligned within region
        right_x = region.right
        weather = state.get(self._weather_entity)
        if weather:
            temp = weather.attribute("temperature")
            ic = WEATHER_ICON.get(weather.state, "·")
            weather_txt = f"{temp:.0f}°C {ic}" if temp is not None else ic
            tw = int(f_reg.getlength(weather_txt))
            right_x -= tw
            draw.text((right_x, region.y + 11), weather_txt, font=f_reg, fill=0)
            right_x -= 12

        refresh_txt = f"↻ {now.strftime('%H:%M')}"
        tw = int(f_reg.getlength(refresh_txt))
        right_x -= tw
        draw.text((right_x, region.y + 11), refresh_txt, font=f_reg, fill=0)
        right_x -= 12

        battery = state.get(self._battery_entity)
        if battery:
            pct_txt = f"{int(float(battery.state))}%"
            tw = int(f_reg.getlength(pct_txt))
            right_x -= tw
            draw.text((right_x, region.y + 11), pct_txt, font=f_reg, fill=0)
            right_x -= 4
            # mini battery box: 18x9, filled width = pct
            box_x = right_x - 18
            draw.rectangle((box_x, region.y + 13, box_x + 18, region.y + 22), outline=0)
            fill_w = int(18 * int(float(battery.state)) / 100)
            draw.rectangle((box_x, region.y + 13, box_x + fill_w, region.y + 22), fill=0)
            right_x = box_x

        # bottom rule
        draw.line((region.x, region.bottom - 1, region.right, region.bottom - 1), fill=0, width=2)
