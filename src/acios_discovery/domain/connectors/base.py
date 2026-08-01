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
    def has_next_page(
        self,
        html: str,
    ) -> bool:
        """
        Returns True if another listing page exists.
        """
