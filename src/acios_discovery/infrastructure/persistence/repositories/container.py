from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .company_repository import (
    SqlAlchemyCompanyRepository,
)
from .crawl_job_repository import (
    SqlAlchemyCrawlJobRepository,
)
from .crawl_session_repository import (
    SqlAlchemyCrawlSessionRepository,
)
from .discovery_repository import (
    SqlAlchemyDiscoveryRepository,
)
from .outbox_repository import (
    SqlAlchemyOutboxRepository,
)
from .company_match_repository import (
    SqlAlchemyCompanyMatchRepository,
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

        self.company_match = (
            SqlAlchemyCompanyMatchRepository(
                session,
            )
        )

        self.discovery = (
            SqlAlchemyDiscoveryRepository(
                session,
            )
        )

        self.outbox = (
            SqlAlchemyOutboxRepository(
                session,
            )
        )

        self.crawl_session = (
            SqlAlchemyCrawlSessionRepository(
                session,
            )
        )


        self.crawl_job = (
            SqlAlchemyCrawlJobRepository(
                session,
            )
        )
