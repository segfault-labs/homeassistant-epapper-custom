"""Weather widget: current temp + icon, 4-day forecast."""
from __future__ import annotations

from datetime import datetime

from epapper.ha_state import HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.fonts import font
from epapper.renderer.layout import Rect

CZECH_DAYS_SHORT = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
CONDITION_LABEL = {
    "sunny": "Slunečno", "clear-night": "Jasno", "cloudy": "Zataženo",
    "partlycloudy": "Polojasno", "rainy": "Déšť", "snowy": "Sníh",
    "fog": "Mlha", "windy": "Větrno", "lightning": "Bouřka",
}
CONDITION_ICON = {
    "sunny": "☀", "clear-night": "☾", "cloudy": "☁", "partlycloudy": "⛅",
    "rainy": "🌧", "snowy": "❄", "fog": "≡", "windy": "⤳", "lightning": "⚡",
}
WIND_DIRS = ["S", "SV", "V", "JV", "J", "JZ", "Z", "SZ"]


class WeatherWidget:
    def __init__(self, weather_entity: str, location: str) -> None:
        self._entity = weather_entity
        self._location = location

    def watched_entities(self) -> list[str]:
        return [self._entity]

    def render(self, canvas: Canvas, region: Rect, state: HAState) -> None:
        draw = canvas.draw
        f_h = font("bold", 11)
        f_temp = font("bold", 44)
        f_ico = font("regular", 40)
        f_desc = font("regular", 11)
        f_fc = font("regular", 11)
        f_fc_b = font("bold", 11)

        draw.text((region.x, region.y + 4), f"{self._location.upper()} · TEĎ", font=f_h, fill=0)

        entity = state.get(self._entity)
        if entity is None:
            draw.text((region.x, region.y + 30), "(no data)", font=f_desc, fill=0)
            return

        condition = entity.state
        temp = entity.attribute("temperature")
        ic = CONDITION_ICON.get(condition, "·")
        draw.text((region.x, region.y + 28), ic, font=f_ico, fill=0)
        if temp is not None:
            draw.text((region.x + 54, region.y + 28), f"{temp:.0f}°", font=f_temp, fill=0)

        desc = CONDITION_LABEL.get(condition, condition)
        wind = entity.attribute("wind_speed")
        bearing = entity.attribute("wind_bearing")
        if wind is not None and bearing is not None:
            dir_label = WIND_DIRS[int((bearing + 22.5) // 45) % 8]
            desc = f"{desc} · vítr {wind:.0f} km/h {dir_label}"
        draw.text((region.x, region.y + 84), desc, font=f_desc, fill=0)

        # 4-day forecast strip
        forecast = entity.attribute("forecast", []) or []
        forecast = forecast[:4]
        if not forecast:
            return
        strip_y = region.y + 110
        draw.line((region.x, strip_y, region.right, strip_y), fill=0)
        col_w = region.w // 4
        for i, day in enumerate(forecast):
            try:
                d = datetime.fromisoformat(day["datetime"])
                d_label = CZECH_DAYS_SHORT[d.weekday()]
            except (KeyError, ValueError):
                d_label = "—"
            cond = day.get("condition", "")
            ic = CONDITION_ICON.get(cond, "·")
            t = day.get("temperature")
            col_x = region.x + col_w * i + col_w // 2

            ic_w = int(font("regular", 18).getlength(ic))
            draw.text((col_x - ic_w // 2, strip_y + 4), ic, font=font("regular", 18), fill=0)
            dl_w = int(f_fc.getlength(d_label))
            draw.text((col_x - dl_w // 2, strip_y + 24), d_label, font=f_fc, fill=0)
            if t is not None:
                t_txt = f"{t:.0f}°"
                tw = int(f_fc_b.getlength(t_txt))
                draw.text((col_x - tw // 2, strip_y + 36), t_txt, font=f_fc_b, fill=0)
