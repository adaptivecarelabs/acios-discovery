import httpx

from acios_discovery.domain.errors.crawl_errors import (
    FatalCrawlError,
    ListingNotFoundError,
    RetryableCrawlError,
)
from acios_discovery.domain.http import HttpClient
from acios_discovery.domain.proxy import Proxy

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class HttpxClient(HttpClient):

    async def get(
        self,
        url: str,
        *,
        proxy: Proxy | None = None,
    ) -> str:

        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=httpx.Timeout(
                    connect=2.0,
                    read=10.0,
                    write=10.0,
                    pool=10.0,
                ),
                proxy=proxy.url if proxy is not None else None,
            ) as client:

                response = await client.get(
                    url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 "
                            "(Macintosh; Intel Mac OS X)"
                        )
                    },
                )

                response.raise_for_status()

                return response.text

        except httpx.TimeoutException as exc:
            raise RetryableCrawlError(
                f"Timeout fetching {url}: {exc}",
            ) from exc

        except (httpx.ConnectError, httpx.NetworkError) as exc:
            raise RetryableCrawlError(
                f"Connection error fetching {url}: {exc}",
            ) from exc

        except httpx.HTTPStatusError as exc:

            status_code = exc.response.status_code

            if status_code in _RETRYABLE_STATUS_CODES:
                raise RetryableCrawlError(
                    f"HTTP {status_code} fetching {url}: {exc}",
                ) from exc

            if status_code == 404:
                raise ListingNotFoundError(
                    f"HTTP 404 fetching {url}: {exc}",
                ) from exc

            raise FatalCrawlError(
                f"HTTP {status_code} fetching {url}: {exc}",
            ) from exc

        except httpx.HTTPError as exc:
            raise FatalCrawlError(
                f"HTTP error fetching {url}: {exc}",
            ) from exc
