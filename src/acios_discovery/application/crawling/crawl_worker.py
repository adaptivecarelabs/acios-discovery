from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.discovery.listing_crawl_result import (
    ListingCrawlResult,
)
from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.domain.crawling import CrawlJob


class CrawlPipeline(Protocol):
    """
    Minimal pipeline contract required by CrawlWorker.

    The worker intentionally depends on the pipeline's execution
    contract rather than its concrete implementation.
    """

    async def execute(
        self,
        job: CrawlJob,
    ) -> DiscoveryRunResult:
        ...


PipelineFactory = Callable[
    [AsyncSession],
    CrawlPipeline,
]


class CrawlWorker:
    """
    Executes one CrawlJob through a database-bound discovery pipeline.

    Every worker execution receives its own AsyncSession.

    The worker never shares a SQLAlchemy AsyncSession with another
    concurrent worker.
    """

    def __init__(
        self,
        *,
        session_factory: Callable[[], AsyncSession],
        pipeline_factory: PipelineFactory,
    ) -> None:
        self._session_factory = session_factory
        self._pipeline_factory = pipeline_factory

    async def execute(
        self,
        job: CrawlJob,
    ) -> ListingCrawlResult:
        async with self._session_factory() as session:
            pipeline = self._pipeline_factory(session)

            result = await pipeline.execute(job)

            await session.commit()

            return ListingCrawlResult(
                pages_crawled=result.pages_crawled,
                companies_discovered=result.records_found,
                records=result.records,
            )
