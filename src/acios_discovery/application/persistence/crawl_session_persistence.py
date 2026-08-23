from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.crawling.crawl_session import CrawlSession


class CrawlSessionPersistence(ABC):
    """
    Persists CrawlSession snapshots without CrawlSupervisor needing
    to know how (or with what session lifetime) that happens.
    """

    @abstractmethod
    async def save(
        self,
        session: CrawlSession,
    ) -> None:
        ...

    @abstractmethod
    async def load(
        self,
        session_id: str,
    ) -> CrawlSession | None:
        ...
