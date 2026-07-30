from abc import ABC, abstractmethod

from acios_discovery.domain.discovery import (
    DiscoveryRecord,
)


class BaseConnector(ABC):
    """
    Every external data source must implement
    this interface.
    """

    @abstractmethod
    async def crawl(
        self,
    ) -> list[DiscoveryRecord]:
        """
        Crawl one source and return
        discovery records.
        """
