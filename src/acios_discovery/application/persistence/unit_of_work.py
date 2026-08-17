from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.repositories.crawl_checkpoint_repository import (
    CrawlCheckpointRepository,
)
from acios_discovery.domain.repositories.crawl_job_repository import (
    CrawlJobRepository,
)
from acios_discovery.domain.repositories.crawl_session_repository import (
    CrawlSessionRepository,
)


class UnitOfWork(ABC):

    discovery_repository: object
    outbox_repository: object

    crawl_session_repository: CrawlSessionRepository
    crawl_checkpoint_repository: CrawlCheckpointRepository
    crawl_job_repository: CrawlJobRepository

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...
