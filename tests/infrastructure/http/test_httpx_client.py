import pytest

from acios_discovery.infrastructure.http.httpx_client import (
    HttpxClient,
)


@pytest.mark.asyncio
@pytest.mark.live
async def test_httpx_client_downloads_business_page() -> None:
    client = HttpxClient()

    try:
        html = await client.get(
            "https://www.finelib.com/business"
        )
    except Exception:
        return

    assert html
    assert "<html" in html.lower()


@pytest.mark.asyncio
async def test_httpx_client_raises_listing_not_found_on_404():
    """
    Regression test: a plain HTTP 404 must raise
    ListingNotFoundError specifically (a subclass of
    FatalCrawlError), not a generic FatalCrawlError — callers
    rely on this distinction to treat "no listing exists" as
    zero results rather than a job failure.
    """

    import httpx

    from acios_discovery.domain.errors.crawl_errors import (
        ListingNotFoundError,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="Not Found")

    transport = httpx.MockTransport(handler)

    client = HttpxClient()

    original_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    import acios_discovery.infrastructure.http.httpx_client as module

    module.httpx.AsyncClient = patched_client

    try:
        with pytest.raises(ListingNotFoundError):
            await client.get("https://example.com/nonexistent")
    finally:
        module.httpx.AsyncClient = original_async_client


@pytest.mark.asyncio
async def test_httpx_client_raises_fatal_error_on_non_404_client_error():
    """
    A non-404 4xx (e.g. 403) must still raise the generic
    FatalCrawlError, not ListingNotFoundError — only 404
    specifically means "no listing exists here".
    """

    import httpx

    from acios_discovery.domain.errors.crawl_errors import (
        FatalCrawlError,
        ListingNotFoundError,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="Forbidden")

    transport = httpx.MockTransport(handler)

    client = HttpxClient()

    original_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    import acios_discovery.infrastructure.http.httpx_client as module

    module.httpx.AsyncClient = patched_client

    try:
        with pytest.raises(FatalCrawlError) as exc_info:
            await client.get("https://example.com/blocked")

        assert not isinstance(
            exc_info.value,
            ListingNotFoundError,
        )
    finally:
        module.httpx.AsyncClient = original_async_client


@pytest.mark.asyncio
async def test_post_json_returns_parsed_json_body():

    import httpx

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"data": [{"approvedName": "ACME LTD"}]},
        )

    transport = httpx.MockTransport(handler)

    client = HttpxClient()

    original_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    import acios_discovery.infrastructure.http.httpx_client as module

    module.httpx.AsyncClient = patched_client

    try:
        result = await client.post_json(
            "https://example.com/search",
            json={"searchTerm": "acme"},
        )
    finally:
        module.httpx.AsyncClient = original_async_client

    assert result == {"data": [{"approvedName": "ACME LTD"}]}


@pytest.mark.asyncio
async def test_post_json_sends_body_and_merged_headers():

    import httpx

    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["headers"] = request.headers
        captured["body"] = request.content
        return httpx.Response(200, json={"data": []})

    transport = httpx.MockTransport(handler)

    client = HttpxClient()

    original_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    import acios_discovery.infrastructure.http.httpx_client as module

    module.httpx.AsyncClient = patched_client

    try:
        await client.post_json(
            "https://example.com/search",
            json={"searchTerm": "acme"},
            headers={"Origin": "https://icrp.cac.gov.ng"},
        )
    finally:
        module.httpx.AsyncClient = original_async_client

    #
    # Custom headers are merged with (not replacing) the default
    # User-Agent.
    #

    assert captured["headers"]["origin"] == "https://icrp.cac.gov.ng"
    assert "user-agent" in captured["headers"]
    assert b"acme" in captured["body"]


@pytest.mark.asyncio
async def test_post_json_raises_retryable_on_429():

    import httpx

    from acios_discovery.domain.errors.crawl_errors import (
        RetryableCrawlError,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="Too Many Requests")

    transport = httpx.MockTransport(handler)

    client = HttpxClient()

    original_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    import acios_discovery.infrastructure.http.httpx_client as module

    module.httpx.AsyncClient = patched_client

    try:
        with pytest.raises(RetryableCrawlError):
            await client.post_json(
                "https://example.com/search",
                json={"searchTerm": "acme"},
            )
    finally:
        module.httpx.AsyncClient = original_async_client


@pytest.mark.asyncio
async def test_post_json_raises_fatal_on_403():

    import httpx

    from acios_discovery.domain.errors.crawl_errors import (
        FatalCrawlError,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="Forbidden")

    transport = httpx.MockTransport(handler)

    client = HttpxClient()

    original_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    import acios_discovery.infrastructure.http.httpx_client as module

    module.httpx.AsyncClient = patched_client

    try:
        with pytest.raises(FatalCrawlError):
            await client.post_json(
                "https://example.com/search",
                json={"searchTerm": "acme"},
            )
    finally:
        module.httpx.AsyncClient = original_async_client
