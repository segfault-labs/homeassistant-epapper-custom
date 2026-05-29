"""1-bit canvas matching the Waveshare 7.5" V2 panel resolution."""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw

WIDTH = 800
HEIGHT = 480
RAW_BYTES_LEN = WIDTH * HEIGHT // 8


@dataclass
class Canvas:
    image: Image.Image

    @classmethod
    def blank(cls) -> Canvas:
        return cls(image=Image.new("1", (WIDTH, HEIGHT), color=1))

    @property
    def draw(self) -> ImageDraw.ImageDraw:
        return ImageDraw.Draw(self.image)

    def to_raw_bytes(self) -> bytes:
        """Pack 1-bit pixels into MSB-first bytes (Waveshare wire format)."""
        return self.image.tobytes()
