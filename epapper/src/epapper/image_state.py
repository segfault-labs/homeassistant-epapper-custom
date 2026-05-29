"""Stores the most recently rendered image and its content-derived ETag.

Used by the HTTP server to decide whether to return 304 to a conditional GET.
"""
from __future__ import annotations

import hashlib
import threading


class ImageState:
    def __init__(self) -> None:
        self._bytes = b""
        self._etag = ""
        self._lock = threading.Lock()

    @property
    def bytes_(self) -> bytes:
        with self._lock:
            return self._bytes

    @property
    def etag(self) -> str:
        with self._lock:
            return self._etag

    def set(self, data: bytes) -> None:
        digest = hashlib.sha256(data).hexdigest()[:16]
        with self._lock:
            self._bytes = data
            self._etag = digest
