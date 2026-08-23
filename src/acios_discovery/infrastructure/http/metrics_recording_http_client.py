from __future__ import annotations

from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.domain.http import HttpClient


class MetricsRecordingHttpClient(HttpClient):
    """
    Wraps an HttpClient, recording every request's outcome
    (sent / succeeded / failed) into CrawlMetricsService.

    This must wrap the HttpClient instance BEFORE it is handed to
    ListingDownloader/FinelibEnricher — those components capture
    their http reference at construction time, so wrapping it
    later would not be observed by already-constructed callers.
    """

    def __init__(
        self,
        *,
        client: HttpClient,
        metrics: CrawlMetricsService,
    ) -> None:
        self._client = client
        self._metrics = metrics

    async def get(
        self,
        url: str,
    ) -> str:

        self._metrics.record_request()

        try:
            result = await self._client.get(url)

        except Exception:
            self._metrics.record_http_failure()
            raise

        self._metrics.record_success()

        return result
