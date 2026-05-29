"""In-memory representation of HA entity state.

Only stores what we need for rendering. Updated by ha_client via state_changed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Entity:
    entity_id: str
    state: str
    attributes: dict[str, Any]

    def attribute(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)


@dataclass
class HAState:
    entities: dict[str, Entity] = field(default_factory=dict)
    # Weather forecasts keyed by entity_id. Stored separately because HA 2024+
    # removed the `forecast` state attribute — it now only comes from the
    # weather.get_forecasts service response.
    forecasts: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def set(self, entity: Entity) -> None:
        self.entities[entity.entity_id] = entity
        self.last_updated = datetime.now(timezone.utc)

    def get(self, entity_id: str) -> Entity | None:
        return self.entities.get(entity_id)

    def set_forecast(self, entity_id: str, forecast: list[dict[str, Any]]) -> None:
        self.forecasts[entity_id] = forecast
        self.last_updated = datetime.now(timezone.utc)

    def get_forecast(self, entity_id: str) -> list[dict[str, Any]]:
        return self.forecasts.get(entity_id, [])
