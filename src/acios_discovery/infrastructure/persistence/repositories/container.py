from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .company_repository import (
    SqlAlchemyCompanyRepository,
)
from .discovery_repository import (
    SqlAlchemyDiscoveryRepository,
)


class PersistenceRepositories:
    """
    Repository collection bound to one database session.

    All repositories created by this object participate
    in the same transaction.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.company = (
            SqlAlchemyCompanyRepository(
                session,
            )
        )

        self.discovery = (
            SqlAlchemyDiscoveryRepository(
                session,
            )
        )
