from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.domain.crawling.crawl_checkpoint import (
    CrawlCheckpoint,
)
from acios_discovery.domain.repositories.crawl_checkpoint_repository import (
    CrawlCheckpointRepository,
)
from acios_discovery.infrastructure.persistence.orm.crawl_checkpoint import (
    CrawlCheckpointORM,
)


class SqlAlchemyCrawlCheckpointRepository(CrawlCheckpointRepository):
    """
    SQLAlchemy repository for crawl checkpoints.

    There is exactly one active checkpoint per crawl session.
    The session_id is therefore the primary key.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def save(
        self,
        checkpoint: CrawlCheckpoint,
    ) -> None:
        orm = await self._session.get(
            CrawlCheckpointORM,
            checkpoint.session_id,
        )

        if orm is None:
            orm = CrawlCheckpointORM(
                session_id=checkpoint.session_id,
                state=checkpoint.state,
                city=checkpoint.city,
                category_slug=checkpoint.category_slug,
                page=checkpoint.page,
                company_index=checkpoint.company_index,
                updated_at=checkpoint.updated_at,
            )

            self._session.add(orm)
            return

        orm.state = checkpoint.state
        orm.city = checkpoint.city
        orm.category_slug = checkpoint.category_slug
        orm.page = checkpoint.page
        orm.company_index = checkpoint.company_index
        orm.updated_at = checkpoint.updated_at

    async def get(
        self,
        session_id: str,
    ) -> CrawlCheckpoint | None:
        stmt = (
            select(CrawlCheckpointORM)
            .where(
                CrawlCheckpointORM.session_id == session_id,
            )
        )

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CrawlCheckpoint(
            session_id=orm.session_id,
            state=orm.state,
            city=orm.city,
            category_slug=orm.category_slug,
            page=orm.page,
            company_index=orm.company_index,
            updated_at=orm.updated_at,
        )

    async def delete(
        self,
        session_id: str,
    ) -> None:
        stmt = (
            delete(CrawlCheckpointORM)
            .where(
                CrawlCheckpointORM.session_id == session_id,
            )
        )

        await self._session.execute(stmt)
