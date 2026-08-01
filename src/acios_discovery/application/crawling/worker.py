from acios_discovery.application.discovery.result import (
    DiscoveryRunResult,
)
from acios_discovery.application.discovery.service import (
    DiscoveryService,
)
from acios_discovery.domain.crawling.status import (
    CrawlStatus,
)
from acios_discovery.domain.queue.job_queue import (
    JobQueue,
)


class CrawlWorker:
    """
    Executes one crawl job.
    """

    def __init__(
        self,
        *,
        service: DiscoveryService,
        queue: JobQueue,
    ) -> None:

        self._service = service
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

        result = await self._service.run(job)

        job.status = CrawlStatus.COMPLETED

        return result
