from epapper.ha_state import Entity, HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.layout import LAYOUT
from epapper.renderer.widgets.weather import WeatherWidget


def _state():
    s = HAState()
    s.set(Entity("weather.home", "sunny", {
        "temperature": 21.0,
        "wind_speed": 8,
        "wind_bearing": 225,
    }))
    # Forecast now lives in HAState.forecasts (from weather.get_forecasts), not
    # in the state attributes.
    s.set_forecast("weather.home", [
        {"datetime": "2026-05-18T00:00:00+02:00", "condition": "partlycloudy", "temperature": 22},
        {"datetime": "2026-05-19T00:00:00+02:00", "condition": "rainy", "temperature": 17},
        {"datetime": "2026-05-20T00:00:00+02:00", "condition": "rainy", "temperature": 15},
        {"datetime": "2026-05-21T00:00:00+02:00", "condition": "sunny", "temperature": 19},
    ])
    return s


def test_weather_watches_entity():
    w = WeatherWidget(weather_entity="weather.home", location="Praha")
    assert w.watched_entities() == ["weather.home"]


def test_weather_renders(assert_snapshot):
    c = Canvas.blank()
    w = WeatherWidget(weather_entity="weather.home", location="Praha")
    w.render(c, LAYOUT["weather"], _state())
    assert_snapshot("widget_weather_default", c.image)


def test_weather_no_forecast(assert_snapshot):
    s = HAState()
    s.set(Entity("weather.home", "sunny", {"temperature": 21.0}))
    c = Canvas.blank()
    w = WeatherWidget(weather_entity="weather.home", location="Praha")
    w.render(c, LAYOUT["weather"], s)
    assert_snapshot("widget_weather_no_forecast", c.image)


def test_weather_entity_missing(assert_snapshot):
    c = Canvas.blank()
    w = WeatherWidget(weather_entity="weather.home", location="Praha")
    w.render(c, LAYOUT["weather"], HAState())
    assert_snapshot("widget_weather_missing", c.image)
