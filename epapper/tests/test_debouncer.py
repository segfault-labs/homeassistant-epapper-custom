import asyncio

import pytest

from epapper.debouncer import Debouncer


@pytest.mark.asyncio
async def test_debouncer_single_call_executes_after_delay():
    calls = []
    async def cb():
        calls.append(1)
    d = Debouncer(delay_s=0.1, callback=cb)
    d.trigger()
    await asyncio.sleep(0.05)
    assert calls == []  # not yet
    await asyncio.sleep(0.1)
    assert calls == [1]


@pytest.mark.asyncio
async def test_debouncer_burst_executes_once():
    calls = []
    async def cb():
        calls.append(1)
    d = Debouncer(delay_s=0.1, callback=cb)
    for _ in range(5):
        d.trigger()
        await asyncio.sleep(0.01)
    await asyncio.sleep(0.2)
    assert calls == [1]


@pytest.mark.asyncio
async def test_debouncer_two_separate_executions():
    calls = []
    async def cb():
        calls.append(1)
    d = Debouncer(delay_s=0.05, callback=cb)
    d.trigger()
    await asyncio.sleep(0.1)
    d.trigger()
    await asyncio.sleep(0.1)
    assert calls == [1, 1]


@pytest.mark.asyncio
async def test_debouncer_propagates_callback_exception_to_log_only():
    calls = []
    async def cb():
        calls.append(1)
        raise RuntimeError("boom")
    d = Debouncer(delay_s=0.05, callback=cb)
    d.trigger()
    await asyncio.sleep(0.1)
    assert calls == [1]
    d.trigger()
    await asyncio.sleep(0.1)
    assert calls == [1, 1]
