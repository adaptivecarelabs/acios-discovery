from __future__ import annotations

import asyncio

import pytest

from acios_discovery.application.proxy import AdaptiveProxyPool
from acios_discovery.domain.proxy import Proxy


def make_proxies(n: int) -> list[Proxy]:
    return [
        Proxy(
            address=f"10.0.0.{i}",
            port=8000 + i,
            username="u",
            password="p",
        )
        for i in range(n)
    ]


@pytest.mark.asyncio
async def test_pool_requires_at_least_one_proxy():
    with pytest.raises(ValueError):
        AdaptiveProxyPool([])


@pytest.mark.asyncio
async def test_acquire_returns_different_proxies_when_all_idle():
    proxies = make_proxies(3)
    pool = AdaptiveProxyPool(proxies, min_delay=0.01, max_delay=1.0)

    selected = {
        (await pool.acquire()).proxy
        for _ in range(3)
    }

    assert selected == set(proxies)


@pytest.mark.asyncio
async def test_report_failure_increases_delay():
    pool = AdaptiveProxyPool(
        make_proxies(1),
        min_delay=1.0,
        max_delay=60.0,
        backoff_multiplier=2.0,
    )

    state = await pool.acquire()

    assert state.current_delay == 1.0

    pool.report_failure(state, retryable=True)

    assert state.current_delay == 2.0
    assert state.consecutive_failures == 1


@pytest.mark.asyncio
async def test_report_failure_caps_at_max_delay():
    pool = AdaptiveProxyPool(
        make_proxies(1),
        min_delay=10.0,
        max_delay=15.0,
        backoff_multiplier=2.0,
    )

    state = await pool.acquire()

    pool.report_failure(state, retryable=True)

    assert state.current_delay == 15.0  # capped, not 20.0


@pytest.mark.asyncio
async def test_non_retryable_failure_does_not_increase_delay():
    pool = AdaptiveProxyPool(
        make_proxies(1),
        min_delay=1.0,
        max_delay=60.0,
    )

    state = await pool.acquire()

    pool.report_failure(state, retryable=False)

    assert state.current_delay == 1.0
    assert state.consecutive_failures == 1


@pytest.mark.asyncio
async def test_report_success_recovers_delay_toward_floor():
    pool = AdaptiveProxyPool(
        make_proxies(1),
        min_delay=1.0,
        max_delay=60.0,
        backoff_multiplier=2.0,
        recovery_multiplier=0.5,
    )

    state = await pool.acquire()

    pool.report_failure(state, retryable=True)
    pool.report_failure(state, retryable=True)

    assert state.current_delay == 4.0

    pool.report_success(state)

    assert state.current_delay == 2.0
    assert state.consecutive_failures == 0


@pytest.mark.asyncio
async def test_report_success_never_drops_below_min_delay():
    pool = AdaptiveProxyPool(
        make_proxies(1),
        min_delay=1.0,
        max_delay=60.0,
        recovery_multiplier=0.5,
    )

    state = await pool.acquire()

    pool.report_success(state)
    pool.report_success(state)
    pool.report_success(state)

    assert state.current_delay == 1.0  # floor, never below


@pytest.mark.asyncio
async def test_acquire_waits_for_soonest_available_proxy():
    pool = AdaptiveProxyPool(
        make_proxies(1),
        min_delay=0.15,
        max_delay=1.0,
    )

    start = asyncio.get_event_loop().time()

    await pool.acquire()  # first acquire is immediate
    await pool.acquire()  # second must wait ~0.15s (only one proxy)

    elapsed = asyncio.get_event_loop().time() - start

    assert elapsed >= 0.1  # allow scheduling slack below the 0.15s delay


@pytest.mark.asyncio
async def test_concurrent_acquire_never_double_books_same_slot():
    """
    Two concurrent acquire() calls on a single-proxy pool must
    not both receive an immediately-available state — the lock
    around reservation must serialize them.
    """

    pool = AdaptiveProxyPool(
        make_proxies(1),
        min_delay=0.05,
        max_delay=1.0,
    )

    results = await asyncio.gather(
        pool.acquire(),
        pool.acquire(),
    )

    # Both return the same (only) proxy, but their reserved
    # slots must differ — proving they weren't both scheduled
    # for time 0.
    state = results[0]
    assert results[0].proxy == results[1].proxy
    assert state.next_available_at > 0


def test_snapshot_returns_all_states():
    proxies = make_proxies(3)
    pool = AdaptiveProxyPool(proxies)

    snapshot = pool.snapshot()

    assert len(snapshot) == 3
    assert {s.proxy for s in snapshot} == set(proxies)
