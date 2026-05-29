from epapper.ha_state import Entity, HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.layout import LAYOUT
from epapper.renderer.widgets.transit import TransitWidget


def _state():
    s = HAState()
    s.set(Entity("sensor.transit_22", "3", {
        "line": "22", "destination": "Bílá Hora",
        "departures": [3, 11, 19],
    }))
    s.set(Entity("sensor.transit_196", "5", {
        "line": "196", "destination": "Smích. nádr.",
        "departures": [5, 17, 32],
    }))
    s.set(Entity("sensor.transit_metro_a", "2", {
        "line": "A", "destination": "Dejvická",
        "departures": [2, 5, 8],
    }))
    return s


def test_transit_watches_all_entities():
    w = TransitWidget(transit_entities=[
        "sensor.transit_22", "sensor.transit_196", "sensor.transit_metro_a"
    ])
    assert "sensor.transit_22" in w.watched_entities()
    assert "sensor.transit_metro_a" in w.watched_entities()


def test_transit_renders(assert_snapshot):
    c = Canvas.blank()
    w = TransitWidget(transit_entities=[
        "sensor.transit_22", "sensor.transit_196", "sensor.transit_metro_a"
    ])
    w.render(c, LAYOUT["transit"], _state())
    assert_snapshot("widget_transit_default", c.image)


def test_transit_missing_entity(assert_snapshot):
    c = Canvas.blank()
    w = TransitWidget(transit_entities=["sensor.missing"])
    w.render(c, LAYOUT["transit"], HAState())
    assert_snapshot("widget_transit_missing", c.image)
