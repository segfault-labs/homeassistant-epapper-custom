"""Snapshot test infrastructure for Pillow images.

Snapshots are PNG files under tests/snapshots/. On first run (or with
UPDATE_SNAPSHOTS=1), the helper writes the snapshot to disk. On subsequent
runs it compares pixel-for-pixel and writes the actual output as <name>.actual.png
on mismatch so you can diff visually.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from PIL import Image, ImageChops

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"
UPDATE = os.environ.get("UPDATE_SNAPSHOTS") == "1"


def _image_equal(a: Image.Image, b: Image.Image) -> bool:
    if a.size != b.size or a.mode != b.mode:
        return False
    # Mode "1" images compare pixel values as 0/1 in memory but 0/255 when
    # loaded from PNG. Normalise both to "L" so ImageChops works correctly.
    if a.mode == "1":
        a = a.convert("L")
        b = b.convert("L")
    diff = ImageChops.difference(a, b)
    return diff.getbbox() is None


@pytest.fixture
def assert_snapshot():
    SNAPSHOT_DIR.mkdir(exist_ok=True)

    def _assert(name: str, image: Image.Image) -> None:
        snap_path = SNAPSHOT_DIR / f"{name}.png"
        if UPDATE or not snap_path.exists():
            image.save(snap_path)
            return
        expected = Image.open(snap_path)
        if not _image_equal(image, expected):
            image.save(SNAPSHOT_DIR / f"{name}.actual.png")
            pytest.fail(
                f"Snapshot mismatch for {name}. "
                f"Compare {name}.png vs {name}.actual.png. "
                f"Run with UPDATE_SNAPSHOTS=1 to accept."
            )

    return _assert
