from __future__ import annotations

from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.infrastructure.persistence.session import (
    session_scope,
)

from .discovery_pipeline import build_pipeline


async def run_discovery(
    job: CrawlJob,
) -> DiscoveryRunResult:
    """
    Execute one discovery job inside one database transaction.

    All repositories used by the pipeline share the same
    AsyncSession.

    Successful execution commits.

    Any exception rolls the transaction back.
    """

    async with session_scope() as session:
        pipeline = build_pipeline(
            session,
        )

        return await pipeline.execute(
            job,
        )
