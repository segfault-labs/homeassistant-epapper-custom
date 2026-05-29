from epapper.ha_state import Entity, HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.layout import LAYOUT
from epapper.renderer.widgets.sensors import SensorsWidget, SensorSpec


def _state():
    s = HAState()
    s.set(Entity("sensor.obyvak_teplota", "22.1", {"unit_of_measurement": "°C"}))
    s.set(Entity("sensor.obyvak_humidity", "45", {"unit_of_measurement": "%"}))
    s.set(Entity("sensor.obyvak_co2", "712", {"unit_of_measurement": "ppm"}))
    s.set(Entity("sensor.venkovni_teplota", "21", {"unit_of_measurement": "°C"}))
    s.set(Entity("sensor.venkovni_pm25", "8", {"unit_of_measurement": "µg/m³"}))
    s.set(Entity("sensor.spot_cena_aktualni", "3.42", {"unit_of_measurement": "Kč/kWh"}))
    return s


def _specs():
    return [
        SensorSpec(title="OBÝVÁK", value_entity="sensor.obyvak_teplota",
                   value_format="{:.0f}°C", subtitle_entity="sensor.obyvak_humidity",
                   subtitle_format="{:.0f}% RH"),
        SensorSpec(title="CO₂", value_entity="sensor.obyvak_co2",
                   value_format="{:.0f}", value_unit="ppm",
                   subtitle="dobré"),
        SensorSpec(title="VENKU", value_entity="sensor.venkovni_teplota",
                   value_format="{:.0f}°C", subtitle_entity="sensor.venkovni_pm25",
                   subtitle_format="PM2.5: {:.0f} µg"),
        SensorSpec(title="EL. CENA", value_entity="sensor.spot_cena_aktualni",
                   value_format="{:.2f}", value_unit="Kč",
                   subtitle="15:00–16:00"),
    ]


def test_sensors_watches_all_entities():
    w = SensorsWidget(specs=_specs())
    watched = w.watched_entities()
    assert "sensor.obyvak_teplota" in watched
    assert "sensor.spot_cena_aktualni" in watched


def test_sensors_renders(assert_snapshot):
    c = Canvas.blank()
    w = SensorsWidget(specs=_specs())
    w.render(c, LAYOUT["sensors"], _state())
    assert_snapshot("widget_sensors_default", c.image)


def test_sensors_missing_value(assert_snapshot):
    c = Canvas.blank()
    w = SensorsWidget(specs=_specs())
    w.render(c, LAYOUT["sensors"], HAState())
    assert_snapshot("widget_sensors_missing", c.image)
