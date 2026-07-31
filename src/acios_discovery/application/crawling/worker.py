from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.domain.connectors.base import (
    BaseConnector,
)
from acios_discovery.domain.crawling.status import (
    CrawlStatus,
)
from acios_discovery.domain.queue.job_queue import (
    JobQueue,
)
from acios_discovery.domain.repositories.discovery_repository import (
    DiscoveryRepository,
)


class CrawlWorker:
    """
    Executes one crawl job.
    """

    def __init__(
        self,
        *,
        connector: BaseConnector,
        repository: DiscoveryRepository,
        queue: JobQueue,
    ) -> None:

        self._connector = connector
        self._repository = repository
        self._queue = queue

    async def run_one_job(
        self,
    ) -> DiscoveryRunResult:

        job = await self._queue.dequeue()

        if job is None:
            return DiscoveryRunResult(
                source="",
                records_found=0,
                records_saved=0,
                duplicates=0,
            )

        job.status = CrawlStatus.RUNNING

        records = await self._connector.crawl(
            job,
        )

        saved = 0
        duplicates = 0

        for record in records:

            if await self._repository.exists(
                record,
            ):
                duplicates += 1
                continue

            await self._repository.save(
                record,
            )

            saved += 1

        job.status = CrawlStatus.COMPLETED

        return DiscoveryRunResult(
            source=job.source,
            records_found=len(records),
            records_saved=saved,
            duplicates=duplicates,
        )
