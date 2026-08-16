import pytest

from acios_discovery.application.discovery.listing_downloader import (
    ListingDownloader,
)


class FakeHttpClient:
    async def get(
        self,
        url: str,
    ) -> str:
        return """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Finelib Business Directory</title>
            </head>
            <body>
                <h1>Business Directory</h1>
            </body>
        </html>
        """


@pytest.mark.asyncio
async def test_listing_downloader_downloads_html() -> None:
    downloader = ListingDownloader(
        FakeHttpClient(),
    )

    html = await downloader.download(
        "https://www.finelib.com/business",
    )

    assert "<html" in html.lower()
    assert "Business Directory" in html
