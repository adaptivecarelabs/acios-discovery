from abc import ABC, abstractmethod

from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.discovery.record import DiscoveryRecord


class BaseConnector(ABC):

    @abstractmethod
    async def crawl(
        self,
        job: CrawlJob,
    ) -> list[DiscoveryRecord]:
        """
        Execute one crawl job.
        """

    @abstractmethod
    def next_page_url(
        self,
        html: str,
        current_url: str,
    ) -> str | None:
        """
        Return the absolute URL of the next listing page.

        Returns None when the current page is the last page.
        """
