from epapper.renderer.canvas import WIDTH, HEIGHT
from epapper.renderer.layout import LAYOUT, Rect


def test_rect_basics():
    r = Rect(x=10, y=20, w=100, h=50)
    assert r.right == 110
    assert r.bottom == 70
    assert r.center == (60, 45)


def test_layout_has_expected_regions():
    assert set(LAYOUT.keys()) == {
        "header", "calendar", "weather", "transit", "todo", "sensors"
    }


def test_layout_regions_fit_inside_canvas():
    for name, rect in LAYOUT.items():
        assert rect.x >= 0, f"{name} starts before x=0"
        assert rect.y >= 0, f"{name} starts before y=0"
        assert rect.right <= WIDTH, f"{name} overflows right edge"
        assert rect.bottom <= HEIGHT, f"{name} overflows bottom edge"


def test_layout_regions_do_not_overlap():
    items = list(LAYOUT.items())
    for i, (n1, r1) in enumerate(items):
        for n2, r2 in items[i + 1:]:
            overlap_x = r1.x < r2.right and r2.x < r1.right
            overlap_y = r1.y < r2.bottom and r2.y < r1.bottom
            assert not (overlap_x and overlap_y), f"{n1} overlaps {n2}"
