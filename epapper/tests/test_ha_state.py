from datetime import datetime, timezone

from epapper.ha_state import HAState, Entity


def test_entity_basic():
    e = Entity(entity_id="weather.home", state="sunny", attributes={"temperature": 21})
    assert e.attribute("temperature") == 21
    assert e.attribute("missing", default=0) == 0


def test_ha_state_empty():
    s = HAState()
    assert s.get("weather.home") is None


def test_ha_state_set_get():
    s = HAState()
    s.set(Entity("weather.home", "sunny", {"temperature": 21}))
    e = s.get("weather.home")
    assert e is not None
    assert e.state == "sunny"


def test_ha_state_last_updated():
    s = HAState()
    before = datetime.now(timezone.utc)
    s.set(Entity("sensor.test", "1", {}))
    assert s.last_updated >= before
