"""App configuration loaded from HA add-on options.json + env (Supervisor token)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from epapper.renderer.widgets.sensors import SensorSpec


@dataclass
class AppConfig:
    refresh_debounce_seconds: int
    calendar_entity: str
    weather_entity: str
    weather_location: str
    todo_nakup_entity: str
    todo_ukoly_entity: str
    battery_entity: str
    transit_entities: list[str]
    sensor_specs: list[SensorSpec]
    log_level: str
    ha_token: str
    ha_ws_url: str
    listen_port: int = 8099

    @classmethod
    def from_file(cls, path: Path) -> "AppConfig":
        raw = json.loads(Path(path).read_text())
        sensors = [
            SensorSpec(
                title=s["title"],
                value_entity=s["value_entity"],
                value_format=s.get("value_format", "{}"),
                value_unit=s.get("value_unit", ""),
                subtitle=s.get("subtitle", ""),
                subtitle_entity=s.get("subtitle_entity"),
                subtitle_format=s.get("subtitle_format", "{}"),
            )
            for s in raw.get("sensors", [])
        ]
        return cls(
            refresh_debounce_seconds=int(raw["refresh_debounce_seconds"]),
            calendar_entity=raw["calendar_entity"],
            weather_entity=raw["weather_entity"],
            weather_location=raw["weather_location"],
            todo_nakup_entity=raw["todo_nakup_entity"],
            todo_ukoly_entity=raw["todo_ukoly_entity"],
            battery_entity=raw["battery_entity"],
            transit_entities=list(raw.get("transit_entities", [])),
            sensor_specs=sensors,
            log_level=raw.get("log_level", "info"),
            ha_token=os.environ.get("SUPERVISOR_TOKEN", ""),
            ha_ws_url=os.environ.get("HA_WS_URL", "ws://supervisor/core/websocket"),
        )

    def all_watched_entities(self) -> set[str]:
        watched = {
            self.calendar_entity, self.weather_entity, self.todo_nakup_entity,
            self.todo_ukoly_entity, self.battery_entity,
        }
        watched.update(self.transit_entities)
        for s in self.sensor_specs:
            watched.add(s.value_entity)
            if s.subtitle_entity:
                watched.add(s.subtitle_entity)
        return watched
