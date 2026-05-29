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
