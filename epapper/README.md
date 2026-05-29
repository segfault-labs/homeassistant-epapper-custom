# e-Paper Renderer (HA Add-on)

Renders a 800×480 1-bit dashboard bitmap from HA state, served over HTTP for
a battery-powered ESP32 e-ink display.

## Installation (HA Green / OS / Supervised)

1. Settings → Add-ons → ⋮ → Repositories
2. Add this repository URL (your local fork or GitHub)
3. Refresh, install "e-Paper Renderer"
4. Configure entities in the Configuration tab:
   - `calendar_entity`: your family calendar
   - `weather_entity`: your weather integration
   - `todo_nakup_entity` + `todo_ukoly_entity`: Todoist / shopping_list entities
   - `battery_entity`: where the ESP32 reports its battery
   - `transit_entities` + `sensors`: see `config.yaml` schema
5. Start the add-on
6. Open the Web UI link to see `/preview.png` and verify rendering

## Endpoints

- `GET /image.bin` — raw 1-bit bitmap (48 000 bytes), with `ETag` header
- `GET /etag` — etag as plain text
- `HEAD /etag` — `If-None-Match` returns 304 when unchanged
- `GET /preview.png` — same image as PNG for debugging (`?force=1` to re-render)
- `GET /health` — JSON status

## Dev loop

```bash
cd epapper-addon
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                     # unit + snapshot tests
UPDATE_SNAPSHOTS=1 pytest  # regenerate snapshots after layout changes
```

Run locally without HA (mock token):

```bash
cat > /tmp/options.json <<EOF
{
  "refresh_debounce_seconds": 5,
  "calendar_entity": "calendar.family",
  "weather_entity": "weather.home",
  "weather_location": "Praha",
  "todo_nakup_entity": "todo.nakup",
  "todo_ukoly_entity": "todo.ukoly",
  "battery_entity": "sensor.epaper_battery_voltage",
  "transit_entities": [],
  "sensors": [],
  "log_level": "info"
}
EOF
OPTIONS_JSON=/tmp/options.json HA_WS_URL=ws://localhost:9999 python -m epapper
```

Open http://localhost:8099/preview.png in your browser.
