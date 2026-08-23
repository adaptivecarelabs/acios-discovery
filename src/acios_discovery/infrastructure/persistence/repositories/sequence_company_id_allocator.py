from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.company.company_id_allocator import (
    CompanyIdAllocator,
)
from acios_discovery.domain.company.company_id import CompanyId


class SequenceCompanyIdAllocator(CompanyIdAllocator):
    """
    Allocates CompanyIds from a Postgres sequence.

    nextval() is atomic at the database level, so concurrent
    workers on separate sessions/transactions can never receive
    the same value — unlike SequentialCompanyIdAllocator, whose
    in-memory counter is private to one process/instance and
    guarantees collisions across concurrent workers.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def allocate(self) -> CompanyId:

        result = await self._session.execute(
            text("SELECT nextval('company_id_seq')"),
        )

        sequence = result.scalar_one()

        return CompanyId.from_sequence(
            sequence,
        )
