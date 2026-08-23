from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
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

        self.crawl_job_repository = (
            repositories.crawl_job
        )

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()


    async def acquire_locks(
        self,
        keys: list[str],
    ) -> None:
        """
        Acquire a Postgres transaction-scoped advisory lock for
        each key, in the given order.

        pg_advisory_xact_lock blocks until the lock is available
        and releases automatically on COMMIT or ROLLBACK — no
        manual unlock is needed, and it composes correctly with
        this class's existing commit()/rollback().

        Callers must pass keys in a deterministic, consistent
        order (see build_resolution_lock_keys) to avoid deadlocks
        between transactions that need overlapping key sets.
        """

        for key in keys:

            await self._session.execute(
                text(
                    "SELECT pg_advisory_xact_lock(hashtext(:key)::bigint)",
                ),
                {"key": key},
            )
