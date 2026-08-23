from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from acios_discovery.application.proxy import AdaptiveProxyPool
from acios_discovery.domain.errors.crawl_errors import (
    FatalCrawlError,
    RetryableCrawlError,
)
from acios_discovery.domain.proxy import Proxy
from acios_discovery.infrastructure.http.proxy_rotating_http_client import (
    ProxyRotatingHttpClient,
)


def make_pool(n: int) -> AdaptiveProxyPool:
    proxies = [
        Proxy(
            address=f"10.0.0.{i}",
            port=8000 + i,
            username="u",
            password="p",
        )
        for i in range(n)
    ]
    return AdaptiveProxyPool(proxies, min_delay=0.001, max_delay=0.01)


@pytest.mark.asyncio
async def test_successful_request_returns_result_on_first_attempt():
    pool = make_pool(3)

    inner = AsyncMock()
    inner.get.return_value = "page content"

    client = ProxyRotatingHttpClient(inner=inner, pool=pool)

    result = await client.get("https://example.com")

    assert result == "page content"
    assert inner.get.call_count == 1


@pytest.mark.asyncio
async def test_retryable_failure_retries_via_different_proxy():
    pool = make_pool(3)

    attempted_proxies = []

    async def fake_get(url, *, proxy=None):
        attempted_proxies.append(proxy)
        if len(attempted_proxies) == 1:
            raise RetryableCrawlError("simulated 429")
        return "ok"

    inner = AsyncMock()
    inner.get.side_effect = fake_get

    client = ProxyRotatingHttpClient(inner=inner, pool=pool)

    result = await client.get("https://example.com")

    assert result == "ok"
    assert inner.get.call_count == 2
    assert attempted_proxies[0] != attempted_proxies[1]


@pytest.mark.asyncio
async def test_fatal_error_raises_immediately_without_retry():
    pool = make_pool(3)

    inner = AsyncMock()
    inner.get.side_effect = FatalCrawlError("simulated 404")

    client = ProxyRotatingHttpClient(inner=inner, pool=pool)

    with pytest.raises(FatalCrawlError):
        await client.get("https://example.com")

    assert inner.get.call_count == 1


@pytest.mark.asyncio
async def test_exhausting_all_attempts_raises_last_retryable_error():
    pool = make_pool(2)

    inner = AsyncMock()
    inner.get.side_effect = RetryableCrawlError("always fails")

    client = ProxyRotatingHttpClient(
        inner=inner,
        pool=pool,
        max_attempts=2,
    )

    with pytest.raises(RetryableCrawlError):
        await client.get("https://example.com")

    assert inner.get.call_count == 2


@pytest.mark.asyncio
async def test_failed_proxy_backs_off_after_retryable_error():
    pool = make_pool(2)

    call_count = 0

    async def fake_get(url, *, proxy=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RetryableCrawlError("simulated 429")
        return "ok"

    inner = AsyncMock()
    inner.get.side_effect = fake_get

    client = ProxyRotatingHttpClient(inner=inner, pool=pool)

    await client.get("https://example.com")

    states = pool.snapshot()
    failed_states = [
        s for s in states if s.consecutive_failures > 0
    ]

    assert len(failed_states) == 1
    assert failed_states[0].current_delay > 0.001  # grew from min_delay
