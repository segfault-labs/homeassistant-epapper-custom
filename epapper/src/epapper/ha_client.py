"""Home Assistant WebSocket client. Subscribes to state_changed and feeds HAState."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Awaitable, Callable

import websockets

from epapper.ha_state import Entity, HAState

log = logging.getLogger(__name__)

_Connect = Callable[[str], Awaitable]


class HAClient:
    def __init__(
        self,
        ws_url: str,
        token: str,
        state: HAState,
        on_relevant_change: Callable[[str], None],
        relevant_entities: set[str],
        _connect: _Connect | None = None,
    ) -> None:
        self._url = ws_url
        self._token = token
        self._state = state
        self._on_relevant = on_relevant_change
        self._relevant = relevant_entities
        self._connect = _connect or websockets.connect
        self._msg_id = 1
        self._states_req_id: int | None = None

    async def run(self) -> None:
        while True:
            try:
                ws = await self._connect(self._url)
                async with ws:
                    await self._handle(ws)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("ha_client disconnected, reconnecting in 5s")
                await asyncio.sleep(5)

    async def _handle(self, ws) -> None:
        # auth
        msg = json.loads(await ws.recv())
        if msg.get("type") != "auth_required":
            raise RuntimeError(f"expected auth_required, got {msg}")
        await ws.send(json.dumps({"type": "auth", "access_token": self._token}))
        msg = json.loads(await ws.recv())
        if msg.get("type") != "auth_ok":
            raise RuntimeError(f"auth failed: {msg}")

        # Subscribe to future changes FIRST, so nothing is missed in the gap
        # between the initial snapshot and the live event stream.
        sub_id = self._next_id()
        await ws.send(json.dumps({
            "id": sub_id,
            "type": "subscribe_events",
            "event_type": "state_changed",
        }))

        # Then fetch the current snapshot of all states. Without this, entities
        # that don't emit a state_changed after we connect (weather, a stable
        # temperature sensor) would never appear and render blank.
        self._states_req_id = self._next_id()
        await ws.send(json.dumps({
            "id": self._states_req_id,
            "type": "get_states",
        }))

        while True:
            raw = await ws.recv()
            self._process(raw)

    def _process(self, raw: str) -> None:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            return

        # Initial get_states snapshot.
        if msg.get("type") == "result":
            if msg.get("id") == self._states_req_id and msg.get("success"):
                for st in msg.get("result") or []:
                    self._ingest(
                        st.get("entity_id"),
                        st.get("state", ""),
                        st.get("attributes") or {},
                    )
            return

        if msg.get("type") != "event":
            return
        event = msg.get("event", {})
        if event.get("event_type") != "state_changed":
            return
        data = event.get("data", {})
        new_state = data.get("new_state") or {}
        self._ingest(
            data.get("entity_id"),
            new_state.get("state", ""),
            new_state.get("attributes", {}) or {},
        )

    def _ingest(self, entity_id, state, attributes) -> None:
        if entity_id is None:
            return
        self._state.set(Entity(
            entity_id=entity_id,
            state=state,
            attributes=attributes,
        ))
        if entity_id in self._relevant:
            self._on_relevant(entity_id)

    def _next_id(self) -> int:
        i = self._msg_id
        self._msg_id += 1
        return i
