from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.crawling.job import CrawlJob


class CrawlJobPersistence(ABC):
    """
    Persists CrawlJob state transitions without the caller needing
    to know how (or with what session lifetime) that happens.
    """

    @abstractmethod
    async def save(
        self,
        job: CrawlJob,
        *,
        session_id: str,
    ) -> None:
        ...
