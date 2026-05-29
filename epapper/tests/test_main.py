import pytest

from epapper.__main__ import build_render_callback
from epapper.config import AppConfig
from epapper.ha_state import HAState
from epapper.image_state import ImageState


@pytest.mark.asyncio
async def test_render_callback_updates_image_state():
    state = HAState()
    image_state = ImageState()
    cfg = AppConfig(
        refresh_debounce_seconds=1,
        calendar_entity="calendar.family",
        weather_entity="weather.home", weather_location="Praha",
        todo_nakup_entity="todo.nakup", todo_ukoly_entity="todo.ukoly",
        battery_entity="sensor.battery",
        transit_entities=[], sensor_specs=[],
        log_level="info", ha_token="x", ha_ws_url="ws://x",
    )
    render = build_render_callback(cfg, state, image_state)
    await render()
    assert len(image_state.bytes_) == 48000
    assert len(image_state.etag) == 16
