import json
from pathlib import Path

from epapper.config import AppConfig


def test_config_loads_from_options_json(tmp_path: Path):
    options = {
        "refresh_debounce_seconds": 30,
        "calendar_entity": "calendar.family",
        "weather_entity": "weather.home",
        "weather_location": "Praha",
        "todo_nakup_entity": "todo.nakup",
        "todo_ukoly_entity": "todo.ukoly",
        "battery_entity": "sensor.epaper_battery",
        "transit_entities": ["sensor.transit_22", "sensor.transit_a"],
        "sensors": [
            {"title": "OBÝVÁK", "value_entity": "sensor.obyvak_teplota",
             "value_format": "{:.0f}°C", "subtitle_entity": "sensor.obyvak_humidity",
             "subtitle_format": "{:.0f}% RH"},
        ],
        "log_level": "info",
    }
    p = tmp_path / "options.json"
    p.write_text(json.dumps(options))

    cfg = AppConfig.from_file(p)
    assert cfg.calendar_entity == "calendar.family"
    assert cfg.refresh_debounce_seconds == 30
    assert len(cfg.transit_entities) == 2
    assert len(cfg.sensor_specs) == 1
    assert cfg.sensor_specs[0].title == "OBÝVÁK"


def test_config_env_overrides(tmp_path, monkeypatch):
    options = {
        "refresh_debounce_seconds": 30, "calendar_entity": "c",
        "weather_entity": "w", "weather_location": "Praha",
        "todo_nakup_entity": "n", "todo_ukoly_entity": "u",
        "battery_entity": "b", "transit_entities": [], "sensors": [],
        "log_level": "info",
    }
    p = tmp_path / "options.json"
    p.write_text(json.dumps(options))
    monkeypatch.setenv("SUPERVISOR_TOKEN", "abc-token-123")
    monkeypatch.setenv("HA_WS_URL", "ws://supervisor/core/websocket")

    cfg = AppConfig.from_file(p)
    assert cfg.ha_token == "abc-token-123"
    assert cfg.ha_ws_url == "ws://supervisor/core/websocket"


def test_config_all_watched_entities_aggregates_everything(tmp_path):
    options = {
        "refresh_debounce_seconds": 30,
        "calendar_entity": "calendar.family",
        "weather_entity": "weather.home",
        "weather_location": "Praha",
        "todo_nakup_entity": "todo.nakup",
        "todo_ukoly_entity": "todo.ukoly",
        "battery_entity": "sensor.battery",
        "transit_entities": ["sensor.transit_22"],
        "sensors": [
            {"title": "X", "value_entity": "sensor.x",
             "subtitle_entity": "sensor.x_sub"},
        ],
        "log_level": "info",
    }
    p = tmp_path / "options.json"
    p.write_text(json.dumps(options))
    cfg = AppConfig.from_file(p)
    watched = cfg.all_watched_entities()
    assert watched == {
        "calendar.family", "weather.home", "todo.nakup", "todo.ukoly",
        "sensor.battery", "sensor.transit_22", "sensor.x", "sensor.x_sub",
    }
