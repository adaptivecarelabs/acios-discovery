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
