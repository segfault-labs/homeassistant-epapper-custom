"""Entry point: wires HA client -> debouncer -> renderer -> ImageState -> HTTP server."""
from __future__ import annotations

import asyncio
import logging
import os
import signal
from pathlib import Path
from typing import Awaitable, Callable

import uvicorn

from epapper.config import AppConfig
from epapper.debouncer import Debouncer
from epapper.ha_client import HAClient
from epapper.ha_state import HAState
from epapper.image_state import ImageState
from epapper.renderer.compose import compose
from epapper.server import build_app

log = logging.getLogger(__name__)


def build_render_callback(
    cfg: AppConfig,
    ha_state: HAState,
    image_state: ImageState,
) -> Callable[[], Awaitable[None]]:
    async def _render() -> None:
        log.info("rendering")
        canvas = compose(
            state=ha_state,
            weather_entity=cfg.weather_entity,
            calendar_entity=cfg.calendar_entity,
            transit_entities=cfg.transit_entities,
            nakup_entity=cfg.todo_nakup_entity,
            ukoly_entity=cfg.todo_ukoly_entity,
            battery_entity=cfg.battery_entity,
            sensor_specs=cfg.sensor_specs,
            location=cfg.weather_location,
        )
        image_state.set(canvas.to_raw_bytes())
        log.info("rendered, etag=%s", image_state.etag)
    return _render


async def amain(cfg: AppConfig) -> None:
    logging.basicConfig(
        level=cfg.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    ha_state = HAState()
    image_state = ImageState()
    render = build_render_callback(cfg, ha_state, image_state)
    debouncer = Debouncer(delay_s=cfg.refresh_debounce_seconds, callback=render)

    client = HAClient(
        ws_url=cfg.ha_ws_url,
        token=cfg.ha_token,
        state=ha_state,
        on_relevant_change=lambda _eid: debouncer.trigger(),
        relevant_entities=cfg.all_watched_entities(),
    )

    # Initial render attempt (will be empty until HA responds, but server is up)
    await render()

    app = build_app(
        image_state=image_state,
        render_now=lambda: asyncio.create_task(render()),
    )
    server_cfg = uvicorn.Config(
        app, host="0.0.0.0", port=cfg.listen_port, log_level=cfg.log_level,
        access_log=False,
    )
    server = uvicorn.Server(server_cfg)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    ha_task = asyncio.create_task(client.run())
    server_task = asyncio.create_task(server.serve())
    stop_task = asyncio.create_task(stop.wait())

    done, pending = await asyncio.wait(
        {ha_task, server_task, stop_task}, return_when=asyncio.FIRST_COMPLETED,
    )
    for t in pending:
        t.cancel()
    log.info("shutting down")


def main() -> None:
    options_path = Path(os.environ.get("OPTIONS_JSON", "/data/options.json"))
    cfg = AppConfig.from_file(options_path)
    asyncio.run(amain(cfg))


if __name__ == "__main__":
    main()
