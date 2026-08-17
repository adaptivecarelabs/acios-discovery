from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.persistence.unit_of_work import (
    UnitOfWork,
)
from acios_discovery.infrastructure.persistence.repositories.container import (
    PersistenceRepositories,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    """
    SQLAlchemy implementation of the application UnitOfWork.

    All repositories are bound to the same AsyncSession, so operations
    performed through the repositories participate in the same
    database transaction.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        repositories = PersistenceRepositories(
            session,
        )

        self.discovery_repository = (
            repositories.discovery
        )

        self.outbox_repository = (
            repositories.outbox
        )

        self.company_repository = (
            repositories.company
        )

        self.crawl_session_repository = (
            repositories.crawl_session
        )

        self.crawl_checkpoint_repository = (
            repositories.crawl_checkpoint
        )

        self.crawl_job_repository = (
            repositories.crawl_job
        )

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
