from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.crawling.job import CrawlJob


class CrawlJobRepository(ABC):
    """
    Domain repository interface for crawl jobs.

    The domain layer defines the persistence contract.
    Infrastructure provides the SQLAlchemy implementation.
    """

    @abstractmethod
    async def save(
        self,
        job: CrawlJob,
        *,
        session_id: str,
    ) -> None:
        ...

    @abstractmethod
    async def get(
        self,
        job_id: str,
    ) -> CrawlJob | None:
        ...

    @abstractmethod
    async def list_by_session(
        self,
        session_id: str,
    ) -> list[CrawlJob]:
        ...

    @abstractmethod
    async def delete(
        self,
        job_id: str,
    ) -> None:
        ...
