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


@pytest.mark.asyncio
async def test_retryable_failure_records_proxy_retry_metric():
    """
    Regression test: a proxy timeout that gets silently absorbed
    and retried via a different proxy must still be visible in
    metrics — otherwise real retry activity (and the time it
    costs) is invisible in the final crawl summary.
    """

    from acios_discovery.application.metrics.crawl_metrics_service import (
        CrawlMetricsService,
    )

    pool = make_pool(3)

    call_count = 0

    async def fake_get(url, *, proxy=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RetryableCrawlError("simulated timeout")
        return "ok"

    inner = AsyncMock()
    inner.get.side_effect = fake_get

    metrics = CrawlMetricsService()

    client = ProxyRotatingHttpClient(
        inner=inner,
        pool=pool,
        metrics=metrics,
    )

    await client.get("https://example.com")

    assert metrics.snapshot().proxy_retries == 1


@pytest.mark.asyncio
async def test_successful_first_attempt_does_not_record_proxy_retry():

    from acios_discovery.application.metrics.crawl_metrics_service import (
        CrawlMetricsService,
    )

    pool = make_pool(3)

    inner = AsyncMock()
    inner.get.return_value = "ok"

    metrics = CrawlMetricsService()

    client = ProxyRotatingHttpClient(
        inner=inner,
        pool=pool,
        metrics=metrics,
    )

    await client.get("https://example.com")

    assert metrics.snapshot().proxy_retries == 0


@pytest.mark.asyncio
async def test_works_without_metrics_service():
    """
    metrics is optional — the client must not raise when no
    metrics service is provided.
    """

    pool = make_pool(2)

    inner = AsyncMock()
    inner.get.return_value = "ok"

    client = ProxyRotatingHttpClient(
        inner=inner,
        pool=pool,
        # metrics intentionally omitted
    )

    result = await client.get("https://example.com")

    assert result == "ok"


@pytest.mark.asyncio
async def test_post_json_returns_result_on_first_attempt():
    pool = make_pool(3)

    inner = AsyncMock()
    inner.post_json.return_value = {"data": []}

    client = ProxyRotatingHttpClient(inner=inner, pool=pool)

    result = await client.post_json(
        "https://example.com/search",
        json={"searchTerm": "acme"},
    )

    assert result == {"data": []}
    assert inner.post_json.call_count == 1


@pytest.mark.asyncio
async def test_post_json_retries_via_different_proxy_on_retryable_error():
    pool = make_pool(3)

    attempted_proxies = []

    async def fake_post_json(url, *, json, headers=None, proxy=None):
        attempted_proxies.append(proxy)
        if len(attempted_proxies) == 1:
            raise RetryableCrawlError("simulated 429")
        return {"data": []}

    inner = AsyncMock()
    inner.post_json.side_effect = fake_post_json

    client = ProxyRotatingHttpClient(inner=inner, pool=pool)

    result = await client.post_json(
        "https://example.com/search",
        json={"searchTerm": "acme"},
    )

    assert result == {"data": []}
    assert inner.post_json.call_count == 2
    assert attempted_proxies[0] != attempted_proxies[1]


@pytest.mark.asyncio
async def test_post_json_raises_fatal_error_immediately_without_retry():
    pool = make_pool(3)

    inner = AsyncMock()
    inner.post_json.side_effect = FatalCrawlError("simulated 403")

    client = ProxyRotatingHttpClient(inner=inner, pool=pool)

    with pytest.raises(FatalCrawlError):
        await client.post_json(
            "https://example.com/search",
            json={"searchTerm": "acme"},
        )

    assert inner.post_json.call_count == 1


@pytest.mark.asyncio
async def test_post_json_exhausting_all_attempts_raises_last_retryable_error():
    pool = make_pool(2)

    inner = AsyncMock()
    inner.post_json.side_effect = RetryableCrawlError("always fails")

    client = ProxyRotatingHttpClient(
        inner=inner,
        pool=pool,
        max_attempts=2,
    )

    with pytest.raises(RetryableCrawlError):
        await client.post_json(
            "https://example.com/search",
            json={"searchTerm": "acme"},
        )

    assert inner.post_json.call_count == 2


@pytest.mark.asyncio
async def test_post_json_forwards_json_and_headers_to_inner():
    pool = make_pool(2)

    inner = AsyncMock()
    inner.post_json.return_value = {"data": []}

    client = ProxyRotatingHttpClient(inner=inner, pool=pool)

    await client.post_json(
        "https://example.com/search",
        json={"searchTerm": "acme"},
        headers={"Origin": "https://icrp.cac.gov.ng"},
    )

    _, kwargs = inner.post_json.call_args

    assert kwargs["json"] == {"searchTerm": "acme"}
    assert kwargs["headers"] == {
        "Origin": "https://icrp.cac.gov.ng",
    }
    assert "proxy" in kwargs
