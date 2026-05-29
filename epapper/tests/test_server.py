from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from epapper.image_state import ImageState
from epapper.server import build_app


@pytest.fixture
def state():
    s = ImageState()
    s.set(b"\xff" * 48000)
    return s


@pytest.fixture
def client(state):
    app = build_app(image_state=state, render_now=lambda: None)
    return TestClient(app)


def test_get_image_returns_bytes(client, state):
    resp = client.get("/image.bin")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/octet-stream"
    assert resp.headers["content-length"] == "48000"
    assert resp.headers["etag"] == state.etag
    assert resp.content == b"\xff" * 48000


def test_get_etag_returns_etag_string(client, state):
    resp = client.get("/etag")
    assert resp.status_code == 200
    assert resp.text == state.etag


def test_head_etag_returns_304_when_match(client, state):
    resp = client.head("/etag", headers={"If-None-Match": state.etag})
    assert resp.status_code == 304


def test_head_etag_returns_200_when_mismatch(client, state):
    resp = client.head("/etag", headers={"If-None-Match": "different"})
    assert resp.status_code == 200


def test_get_image_returns_304_when_etag_matches(client, state):
    resp = client.get("/image.bin", headers={"If-None-Match": state.etag})
    assert resp.status_code == 304
    assert resp.content == b""


def test_preview_png_returns_png(client, state):
    resp = client.get("/preview.png")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    img = Image.open(BytesIO(resp.content))
    assert img.size == (800, 480)


def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "etag" in body


def test_preview_force_triggers_render():
    state = ImageState()
    state.set(b"\xff" * 48000)
    rendered = []
    app = build_app(image_state=state, render_now=lambda: rendered.append(1))
    client = TestClient(app)
    client.get("/preview.png?force=1")
    assert rendered == [1]
