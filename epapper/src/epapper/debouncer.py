"""Async debouncer: collapses bursts of triggers into a single delayed execution."""
from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable

log = logging.getLogger(__name__)


class Debouncer:
    def __init__(self, delay_s: float, callback: Callable[[], Awaitable[None]]) -> None:
        self._delay = delay_s
        self._callback = callback
        self._task: asyncio.Task | None = None

    def trigger(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        try:
            await asyncio.sleep(self._delay)
            await self._callback()
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("debouncer callback raised")
