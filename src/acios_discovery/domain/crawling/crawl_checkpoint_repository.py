from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.crawling.crawl_checkpoint import (
    CrawlCheckpoint,
)


class CrawlCheckpointRepository(ABC):
    """
    Repository abstraction for crawl checkpoints.
    """

    @abstractmethod
    async def save(
        self,
        checkpoint: CrawlCheckpoint,
    ) -> None:
        ...

    @abstractmethod
    async def get(
        self,
        session_id: str,
    ) -> CrawlCheckpoint | None:
        ...

    @abstractmethod
    async def delete(
        self,
        session_id: str,
    ) -> None:
        ...
