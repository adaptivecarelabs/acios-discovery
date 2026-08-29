from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.domain.cac import CacVerificationResult, VerificationOutcome
from acios_discovery.domain.repositories.cac_verification_repository import (
    CacVerificationRepository,
)
from acios_discovery.infrastructure.persistence.mappers.cac_verification_mapper import (
    CacVerificationMapper,
)
from acios_discovery.infrastructure.persistence.orm.cac_verification import (
    CacVerificationORM,
)


class SqlAlchemyCacVerificationRepository(CacVerificationRepository):
    """
    SQLAlchemy implementation of CacVerificationRepository.

    Operates on an externally supplied AsyncSession so it
    participates in the caller's transaction.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def add(
        self,
        result: CacVerificationResult,
    ) -> None:

        orm = CacVerificationMapper.to_orm(result)

        self._session.add(orm)

    async def get_latest_for_company(
        self,
        company_id: str,
    ) -> CacVerificationResult | None:

        stmt = (
            select(CacVerificationORM)
            .where(
                CacVerificationORM.company_id == company_id,
            )
            .order_by(
                CacVerificationORM.verified_at.desc(),
            )
            .limit(1)
        )

        result = await self._session.execute(stmt)

        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return CacVerificationMapper.to_domain(orm)

    async def get_terminal_company_ids(
        self,
    ) -> set[str]:

        terminal_outcomes = (
            VerificationOutcome.VERIFIED.value,
            VerificationOutcome.NOT_FOUND.value,
        )

        stmt = (
            select(CacVerificationORM.company_id)
            .distinct()
            .where(
                CacVerificationORM.outcome.in_(terminal_outcomes),
            )
        )

        result = await self._session.execute(stmt)

        return set(result.scalars().all())
