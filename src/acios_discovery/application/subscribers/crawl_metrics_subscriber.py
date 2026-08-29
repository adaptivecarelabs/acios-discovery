from __future__ import annotations

from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.domain.events.company_discovered_event import (
    CompanyDiscoveredEvent,
)
from acios_discovery.domain.events.company_merged_event import (
    CompanyMergedEvent,
)
from acios_discovery.domain.events.job_completed_event import (
    JobCompletedEvent,
)
from acios_discovery.domain.events.job_failed_event import JobFailedEvent
from acios_discovery.domain.events.job_retried_event import JobRetriedEvent
from acios_discovery.domain.events.page_crawled_event import (
    PageCrawledEvent,
)


class CrawlMetricsSubscriber:
    """
    Updates crawl metrics
    from published crawl events.
    """

    def __init__(
        self,
        metrics: CrawlMetricsService,
    ) -> None:

        self._metrics = metrics

    async def __call__(
        self,
        event,
    ) -> None:

        if isinstance(
            event,
            JobCompletedEvent,
        ):
            self._metrics.record_job_processed()

        elif isinstance(
            event,
            PageCrawledEvent,
        ):
            self._metrics.record_page()

        elif isinstance(
            event,
            CompanyDiscoveredEvent,
        ):
            self._metrics.record_company()

        elif isinstance(
            event,
            CompanyMergedEvent,
        ):
            self._metrics.record_duplicate()

        elif isinstance(
            event,
            JobRetriedEvent,
        ):
            self._metrics.record_retry()

        elif isinstance(
            event,
            JobFailedEvent,
        ):
            self._metrics.record_failure()
