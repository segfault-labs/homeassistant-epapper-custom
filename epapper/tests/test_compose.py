from datetime import datetime, timezone

from epapper.ha_state import Entity, HAState
from epapper.renderer.canvas import RAW_BYTES_LEN
from epapper.renderer.compose import compose
from epapper.renderer.widgets.sensors import SensorSpec


def _full_state():
    s = HAState()
    s.set(Entity("weather.home", "sunny", {
        "temperature": 21.0, "wind_speed": 8, "wind_bearing": 225,
        "forecast": [
            {"datetime": "2026-05-18T00:00:00+02:00", "condition": "partlycloudy", "temperature": 22},
            {"datetime": "2026-05-19T00:00:00+02:00", "condition": "rainy", "temperature": 17},
            {"datetime": "2026-05-20T00:00:00+02:00", "condition": "rainy", "temperature": 15},
            {"datetime": "2026-05-21T00:00:00+02:00", "condition": "sunny", "temperature": 19},
        ],
    }))
    s.set(Entity("calendar.family", "on", {
        "all_events": [
            {"summary": "Doktor Novák",
             "start": "2026-05-17T14:00:00+00:00",
             "end": "2026-05-17T15:00:00+00:00",
             "location": "Praha 4"},
            {"summary": "Vyzvednout Klárku",
             "start": "2026-05-17T16:30:00+00:00",
             "end": "2026-05-17T17:00:00+00:00",
             "location": "ZŠ"},
            {"summary": "Tenis",
             "start": "2026-05-17T18:30:00+00:00",
             "end": "2026-05-17T19:30:00+00:00",
             "location": "klub"},
        ],
    }))
    for line, dst, deps in [
        ("22", "Bílá Hora", [3, 11, 19]),
        ("196", "Smích. nádr.", [5, 17, 32]),
        ("A", "Dejvická", [2, 5, 8]),
    ]:
        s.set(Entity(f"sensor.transit_{line.lower()}", str(deps[0]), {
            "line": line, "destination": dst, "departures": deps,
        }))
    s.set(Entity("todo.nakup", "12", {
        "items": [{"summary": x, "status": "needs_action"} for x in [
            "Mléko 1,5 % (2×)", "Chleba kváskový", "Jogurt bílý 500 g",
            "Banány", "Máslo", "Káva", "Cibule", "Mrkev", "Brambory",
            "Vejce", "Olej", "Pomeranče",
        ]],
    }))
    s.set(Entity("todo.ukoly", "5", {
        "items": [{"summary": x, "status": "needs_action"} for x in [
            "Zaplatit pojištění (do Po)", "Domluvit servis kola",
            "Vyzvednout balík", "Zavolat doktorovi", "Spravit kohoutek",
        ]],
    }))
    s.set(Entity("sensor.obyvak_teplota", "22.1", {}))
    s.set(Entity("sensor.obyvak_humidity", "45", {}))
    s.set(Entity("sensor.obyvak_co2", "712", {}))
    s.set(Entity("sensor.venkovni_teplota", "21", {}))
    s.set(Entity("sensor.venkovni_pm25", "8", {}))
    s.set(Entity("sensor.spot_cena_aktualni", "3.42", {}))
    s.set(Entity("sensor.epaper_battery_voltage", "72", {}))
    return s


def _now():
    return datetime(2026, 5, 17, 14, 32, tzinfo=timezone.utc)


def _sensor_specs():
    return [
        SensorSpec(title="OBÝVÁK", value_entity="sensor.obyvak_teplota",
                   value_format="{:.0f}°C", subtitle_entity="sensor.obyvak_humidity",
                   subtitle_format="{:.0f}% RH"),
        SensorSpec(title="CO₂", value_entity="sensor.obyvak_co2",
                   value_format="{:.0f}", value_unit="ppm", subtitle="dobré"),
        SensorSpec(title="VENKU", value_entity="sensor.venkovni_teplota",
                   value_format="{:.0f}°C", subtitle_entity="sensor.venkovni_pm25",
                   subtitle_format="PM2.5: {:.0f} µg"),
        SensorSpec(title="EL. CENA", value_entity="sensor.spot_cena_aktualni",
                   value_format="{:.2f}", value_unit="Kč", subtitle="15:00–16:00"),
    ]


def test_compose_full_dashboard(assert_snapshot):
    canvas = compose(
        state=_full_state(),
        weather_entity="weather.home",
        calendar_entity="calendar.family",
        transit_entities=["sensor.transit_22", "sensor.transit_196", "sensor.transit_a"],
        nakup_entity="todo.nakup",
        ukoly_entity="todo.ukoly",
        battery_entity="sensor.epaper_battery_voltage",
        sensor_specs=_sensor_specs(),
        location="Praha",
        now=_now,
    )
    assert_snapshot("compose_full_dashboard", canvas.image)


def test_compose_returns_canvas_with_correct_bytes():
    canvas = compose(
        state=_full_state(),
        weather_entity="weather.home",
        calendar_entity="calendar.family",
        transit_entities=[],
        nakup_entity="todo.nakup",
        ukoly_entity="todo.ukoly",
        battery_entity="sensor.epaper_battery_voltage",
        sensor_specs=_sensor_specs(),
        location="Praha",
        now=_now,
    )
    assert len(canvas.to_raw_bytes()) == RAW_BYTES_LEN
