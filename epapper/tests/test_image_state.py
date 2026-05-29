from epapper.image_state import ImageState


def test_image_state_empty_initial():
    s = ImageState()
    assert s.bytes_ == b""
    assert s.etag == ""


def test_image_state_set_updates_etag():
    s = ImageState()
    s.set(b"\xff" * 1000)
    assert s.bytes_ == b"\xff" * 1000
    assert len(s.etag) == 16
    assert all(c in "0123456789abcdef" for c in s.etag)


def test_image_state_same_bytes_same_etag():
    s1 = ImageState()
    s2 = ImageState()
    s1.set(b"hello")
    s2.set(b"hello")
    assert s1.etag == s2.etag


def test_image_state_different_bytes_different_etag():
    s = ImageState()
    s.set(b"hello")
    e1 = s.etag
    s.set(b"world")
    assert s.etag != e1
