from datetime import datetime, timezone

from epapper.ha_state import Entity, HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.layout import LAYOUT
from epapper.renderer.widgets.header import HeaderWidget


def _state(weather_state="sunny", weather_temp=21.0, battery=72):
    s = HAState()
    s.set(Entity("weather.home", weather_state, {"temperature": weather_temp}))
    s.set(Entity("sensor.epaper_battery_voltage", str(battery), {"unit_of_measurement": "%"}))
    return s


def test_header_watches_weather_and_battery():
    w = HeaderWidget(
        weather_entity="weather.home",
        battery_entity="sensor.epaper_battery_voltage",
        now=lambda: datetime(2026, 5, 17, 14, 32, tzinfo=timezone.utc),
    )
    assert "weather.home" in w.watched_entities()
    assert "sensor.epaper_battery_voltage" in w.watched_entities()


def test_header_renders_snapshot(assert_snapshot):
    canvas = Canvas.blank()
    w = HeaderWidget(
        weather_entity="weather.home",
        battery_entity="sensor.epaper_battery_voltage",
        now=lambda: datetime(2026, 5, 17, 14, 32, tzinfo=timezone.utc),
    )
    w.render(canvas, LAYOUT["header"], _state())
    assert_snapshot("widget_header_default", canvas.image)


def test_header_handles_missing_weather(assert_snapshot):
    canvas = Canvas.blank()
    s = HAState()
    s.set(Entity("sensor.epaper_battery_voltage", "30", {}))
    w = HeaderWidget(
        weather_entity="weather.home",
        battery_entity="sensor.epaper_battery_voltage",
        now=lambda: datetime(2026, 5, 17, 14, 32, tzinfo=timezone.utc),
    )
    w.render(canvas, LAYOUT["header"], s)
    assert_snapshot("widget_header_no_weather", canvas.image)
