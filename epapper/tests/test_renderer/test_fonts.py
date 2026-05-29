from epapper.renderer.fonts import font


def test_font_returns_pillow_font():
    f = font("regular", 14)
    assert f.getlength("Hello") > 0


def test_font_caches_same_instance():
    a = font("regular", 14)
    b = font("regular", 14)
    assert a is b


def test_font_bold_differs_from_regular():
    r = font("regular", 14)
    b = font("bold", 14)
    assert r is not b
