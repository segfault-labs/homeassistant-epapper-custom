"""Top-level renderer — wires widgets into the canvas in their layout regions."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from epapper.ha_state import HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.layout import LAYOUT
from epapper.renderer.widgets.calendar import CalendarWidget
from epapper.renderer.widgets.header import HeaderWidget
from epapper.renderer.widgets.sensors import SensorsWidget, SensorSpec
from epapper.renderer.widgets.todo import TodoWidget
from epapper.renderer.widgets.transit import TransitWidget
from epapper.renderer.widgets.weather import WeatherWidget


def compose(
    state: HAState,
    *,
    weather_entity: str,
    calendar_entity: str,
    transit_entities: list[str],
    nakup_entity: str,
    ukoly_entity: str,
    battery_entity: str,
    sensor_specs: list[SensorSpec],
    location: str,
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> Canvas:
    canvas = Canvas.blank()

    HeaderWidget(weather_entity=weather_entity, battery_entity=battery_entity, now=now) \
        .render(canvas, LAYOUT["header"], state)
    CalendarWidget(calendar_entity=calendar_entity, now=now) \
        .render(canvas, LAYOUT["calendar"], state)
    WeatherWidget(weather_entity=weather_entity, location=location) \
        .render(canvas, LAYOUT["weather"], state)
    TransitWidget(transit_entities=transit_entities) \
        .render(canvas, LAYOUT["transit"], state)
    TodoWidget(nakup_entity=nakup_entity, ukoly_entity=ukoly_entity) \
        .render(canvas, LAYOUT["todo"], state)
    SensorsWidget(specs=sensor_specs) \
        .render(canvas, LAYOUT["sensors"], state)

    return canvas
