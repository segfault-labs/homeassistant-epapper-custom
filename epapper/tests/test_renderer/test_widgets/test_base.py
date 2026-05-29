from epapper.renderer.canvas import Canvas
from epapper.renderer.layout import Rect
from epapper.renderer.widgets.base import Widget
from epapper.ha_state import HAState


class _DummyWidget:
    def watched_entities(self) -> list[str]:
        return ["sensor.dummy"]

    def render(self, canvas, region, state):
        canvas.draw.rectangle((region.x, region.y, region.right, region.bottom), fill=0)


def test_dummy_satisfies_widget_protocol():
    w: Widget = _DummyWidget()
    assert w.watched_entities() == ["sensor.dummy"]


def test_widget_can_draw_into_region():
    w = _DummyWidget()
    c = Canvas.blank()
    r = Rect(10, 10, 50, 50)
    w.render(c, r, HAState())
    assert c.image.getpixel((20, 20)) == 0  # filled black
    assert c.image.getpixel((100, 100)) == 1  # untouched white
