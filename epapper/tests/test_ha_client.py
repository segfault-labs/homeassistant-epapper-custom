import asyncio
import json

import pytest

from epapper.ha_client import HAClient
from epapper.ha_state import HAState


class _MockWS:
    """Minimal mock of websockets connection."""
    def __init__(self, scripted_messages: list[str]) -> None:
        self._scripted = list(scripted_messages)
        self.sent: list[str] = []
        self._closed = False

    async def send(self, msg: str) -> None:
        self.sent.append(msg)

    async def recv(self) -> str:
        if not self._scripted:
            await asyncio.sleep(3600)  # block forever
            raise RuntimeError("unreachable")
        return self._scripted.pop(0)

    async def close(self) -> None:
        self._closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


@pytest.mark.asyncio
async def test_ha_client_authenticates_and_subscribes():
    ws = _MockWS([
        json.dumps({"type": "auth_required"}),
        json.dumps({"type": "auth_ok"}),
        json.dumps({"id": 1, "type": "result", "success": True}),
        json.dumps({
            "id": 1, "type": "event",
            "event": {"event_type": "state_changed", "data": {
                "entity_id": "weather.home",
                "new_state": {"state": "sunny", "attributes": {"temperature": 21}}
            }}
        }),
    ])
    state = HAState()
    triggered: list[str] = []

    async def fake_connect(url):
        return ws

    client = HAClient(
        ws_url="ws://test/api/websocket",
        token="test-token",
        state=state,
        on_relevant_change=lambda eid: triggered.append(eid),
        relevant_entities={"weather.home"},
        _connect=fake_connect,
    )
    task = asyncio.create_task(client.run())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Auth payload sent
    assert any('"type": "auth"' in s and '"test-token"' in s for s in ws.sent)
    # Subscribe payload sent
    assert any("subscribe_events" in s for s in ws.sent)
    # State updated
    assert state.get("weather.home").attribute("temperature") == 21
    # Trigger fired
    assert triggered == ["weather.home"]


@pytest.mark.asyncio
async def test_ha_client_fetches_initial_states():
    # Regression: entities that never emit a state_changed after the add-on
    # starts (weather, a stable temperature sensor) must still be populated
    # from the initial get_states snapshot. Note: no state_changed events here.
    ws = _MockWS([
        json.dumps({"type": "auth_required"}),
        json.dumps({"type": "auth_ok"}),
        # subscribe ack (id=1), ignored
        json.dumps({"id": 1, "type": "result", "success": True}),
        # get_states result (id=2)
        json.dumps({"id": 2, "type": "result", "success": True, "result": [
            {"entity_id": "weather.home", "state": "cloudy",
             "attributes": {"temperature": 9}},
            {"entity_id": "sensor.obyvak_teplota", "state": "21.5",
             "attributes": {"unit_of_measurement": "°C"}},
            {"entity_id": "sensor.unwatched", "state": "x", "attributes": {}},
        ]}),
    ])
    state = HAState()
    triggered: list[str] = []

    async def fake_connect(url):
        return ws

    client = HAClient(
        ws_url="ws://test/api/websocket",
        token="t",
        state=state,
        on_relevant_change=lambda eid: triggered.append(eid),
        relevant_entities={"weather.home", "sensor.obyvak_teplota"},
        _connect=fake_connect,
    )
    task = asyncio.create_task(client.run())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # get_states request was sent
    assert any('"get_states"' in s for s in ws.sent)
    # initial snapshot populated without any state_changed event
    assert state.get("weather.home").attribute("temperature") == 9
    assert state.get("sensor.obyvak_teplota").state == "21.5"
    assert state.get("sensor.unwatched") is not None
    # only relevant entities fired the redraw trigger
    assert set(triggered) == {"weather.home", "sensor.obyvak_teplota"}


@pytest.mark.asyncio
async def test_ha_client_fetches_forecast():
    # Forecast comes from the weather.get_forecasts service, not state attributes.
    # ids: subscribe=1, get_states=2, get_forecasts=3.
    ws = _MockWS([
        json.dumps({"type": "auth_required"}),
        json.dumps({"type": "auth_ok"}),
        json.dumps({"id": 2, "type": "result", "success": True, "result": []}),
        json.dumps({"id": 3, "type": "result", "success": True, "result": {
            "response": {"weather.home": {"forecast": [
                {"datetime": "2026-05-30T00:00:00", "condition": "sunny", "temperature": 25},
                {"datetime": "2026-05-31T00:00:00", "condition": "rainy", "temperature": 18},
            ]}},
        }}),
    ])
    state = HAState()
    triggered: list[str] = []

    async def fake_connect(url):
        return ws

    client = HAClient(
        ws_url="ws://test/api/websocket",
        token="t",
        state=state,
        on_relevant_change=lambda eid: triggered.append(eid),
        relevant_entities={"weather.home"},
        weather_entities=["weather.home"],
        _connect=fake_connect,
    )
    task = asyncio.create_task(client.run())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # get_forecasts service call was sent
    assert any('"get_forecasts"' in s for s in ws.sent)
    # forecast stored on state
    fc = state.get_forecast("weather.home")
    assert len(fc) == 2
    assert fc[0]["condition"] == "sunny" and fc[1]["temperature"] == 18
    # redraw trigger fired for the weather entity
    assert "weather.home" in triggered


@pytest.mark.asyncio
async def test_ha_client_ignores_irrelevant_entities():
    ws = _MockWS([
        json.dumps({"type": "auth_required"}),
        json.dumps({"type": "auth_ok"}),
        json.dumps({"id": 1, "type": "result", "success": True}),
        json.dumps({
            "id": 1, "type": "event",
            "event": {"event_type": "state_changed", "data": {
                "entity_id": "sensor.something_else",
                "new_state": {"state": "x", "attributes": {}}
            }}
        }),
    ])
    state = HAState()
    triggered: list[str] = []

    async def fake_connect(url):
        return ws

    client = HAClient(
        ws_url="ws://test/api/websocket",
        token="t",
        state=state,
        on_relevant_change=lambda eid: triggered.append(eid),
        relevant_entities={"weather.home"},
        _connect=fake_connect,
    )
    task = asyncio.create_task(client.run())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    # State STILL captured (we track everything we see)
    assert state.get("sensor.something_else") is not None
    # But no trigger
    assert triggered == []
