import pytest

from acios_discovery.application.discovery.listing_downloader import (
    ListingDownloader,
)
from acios_discovery.infrastructure.http.httpx_client import (
    HttpxClient,
)


@pytest.mark.asyncio
async def test_listing_downloader_downloads_html() -> None:

    downloader = ListingDownloader(
        HttpxClient(),
    )

    html = await downloader.download(
        "https://www.finelib.com/business"
    )

    assert "<html" in html.lower()

    assert len(html) > 1000
