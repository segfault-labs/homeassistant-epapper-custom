"""Cached Pillow font loader for embedded Inter TTF."""
from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from typing import Literal

from PIL import ImageFont

Weight = Literal["regular", "bold"]

_FILES = {
    "regular": "Inter-Regular.ttf",
    "bold": "Inter-Bold.ttf",
}


@lru_cache(maxsize=64)
def font(weight: Weight, size: int) -> ImageFont.FreeTypeFont:
    asset = files("epapper.renderer.assets") / _FILES[weight]
    with asset.open("rb") as fh:
        return ImageFont.truetype(fh, size=size)
