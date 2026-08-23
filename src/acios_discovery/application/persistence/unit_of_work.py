from __future__ import annotations

from abc import ABC, abstractmethod

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


    async def acquire_locks(
        self,
        keys: list[str],
    ) -> None:
        """
        Acquire exclusive, transaction-scoped locks for the given
        keys, held until this unit of work commits or rolls back.

        Default is a no-op. Only implementations backed by a real
        database, which can provide genuine cross-transaction
        locking, need to override this.
        """
        return None
