from epapper.renderer.canvas import Canvas, WIDTH, HEIGHT, RAW_BYTES_LEN


def test_canvas_dimensions():
    assert WIDTH == 800
    assert HEIGHT == 480
    assert RAW_BYTES_LEN == 48_000  # 800*480/8


def test_canvas_creates_white_1bit_image():
    canvas = Canvas.blank()
    assert canvas.image.mode == "1"
    assert canvas.image.size == (WIDTH, HEIGHT)
    # all white = all 1s in mode "1"
    assert canvas.image.getpixel((0, 0)) == 1
    assert canvas.image.getpixel((WIDTH - 1, HEIGHT - 1)) == 1


def test_canvas_to_raw_bytes_returns_exactly_48000():
    canvas = Canvas.blank()
    data = canvas.to_raw_bytes()
    assert isinstance(data, bytes)
    assert len(data) == RAW_BYTES_LEN


def test_canvas_to_raw_bytes_all_white_is_ff():
    canvas = Canvas.blank()
    data = canvas.to_raw_bytes()
    assert data == b"\xff" * RAW_BYTES_LEN
