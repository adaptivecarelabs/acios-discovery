from abc import ABC, abstractmethod

from acios_discovery.domain.crawling.crawl_session import CrawlSession


class CrawlSessionRepository(ABC):
    """
    Repository for crawl sessions.
    """

    @abstractmethod
    async def save(
        self,
        session: CrawlSession,
    ) -> None:
        ...

    @abstractmethod
    async def get(
        self,
        session_id: str,
    ) -> CrawlSession | None:
        ...

    @abstractmethod
    async def list_all(
        self,
    ) -> list[CrawlSession]:
        ...

    @abstractmethod
    async def delete(
        self,
        session_id: str,
    ) -> None:
        ...
