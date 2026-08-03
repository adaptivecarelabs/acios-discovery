import pytest

from acios_discovery.infrastructure.http.httpx_client import (
    HttpxClient,
)


@pytest.mark.asyncio
async def test_httpx_client_downloads_business_page() -> None:

    client = HttpxClient()

    html = await client.get(
        "https://www.finelib.com/business"
    )

    assert isinstance(html, str)

    assert len(html) > 1000

    assert "<html" in html.lower()
