from acios_discovery.domain.events.company_discovered_event import (
    CompanyDiscoveredEvent,
)
from acios_discovery.domain.events.job_completed_event import (
    JobCompletedEvent,
)
from acios_discovery.domain.events.page_crawled_event import (
    PageCrawledEvent,
)


class MetricsEventSubscriber:
    """
    Updates runtime metrics from crawl events.
    """

    def __init__(
        self,
        metrics,
    ) -> None:

        self._metrics = metrics

    def __call__(
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
