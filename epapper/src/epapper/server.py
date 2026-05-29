"""FastAPI server exposing the rendered image to ESP32.

Note: render is unpacked from raw 1-bit bytes back to a PIL image for /preview.png.
"""
from __future__ import annotations

import io
from typing import Callable

from fastapi import FastAPI, Header, Response
from fastapi.responses import PlainTextResponse, StreamingResponse
from PIL import Image

from epapper.image_state import ImageState
from epapper.renderer.canvas import HEIGHT, WIDTH


def build_app(image_state: ImageState, render_now: Callable[[], None]) -> FastAPI:
    app = FastAPI(title="epapper", version="0.1.0")

    @app.get("/image.bin")
    def get_image(if_none_match: str | None = Header(default=None, alias="If-None-Match")):
        if if_none_match and if_none_match == image_state.etag:
            return Response(status_code=304)
        return Response(
            content=image_state.bytes_,
            media_type="application/octet-stream",
            headers={"ETag": image_state.etag, "Cache-Control": "no-store"},
        )

    @app.head("/etag")
    def head_etag(if_none_match: str | None = Header(default=None, alias="If-None-Match")):
        if if_none_match and if_none_match == image_state.etag:
            return Response(status_code=304)
        return Response(status_code=200, headers={"ETag": image_state.etag})

    @app.get("/etag", response_class=PlainTextResponse)
    def get_etag():
        return image_state.etag

    @app.get("/preview.png")
    def get_preview(force: int = 0):
        if force:
            render_now()
        data = image_state.bytes_
        if len(data) != WIDTH * HEIGHT // 8:
            return Response(status_code=503, content=b"no image yet")
        img = Image.frombytes("1", (WIDTH, HEIGHT), data)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return StreamingResponse(io.BytesIO(buf.getvalue()), media_type="image/png")

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "etag": image_state.etag,
            "image_size": len(image_state.bytes_),
        }

    return app
