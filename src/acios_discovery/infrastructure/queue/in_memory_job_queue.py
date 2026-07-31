from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.queue.job_queue import JobQueue


class InMemoryJobQueue(JobQueue):
    """
    Simple FIFO queue.
    """

    def __init__(self) -> None:
        self._jobs: list[CrawlJob] = []

    async def enqueue(
        self,
        job: CrawlJob,
    ) -> None:
        self._jobs.append(job)

    async def dequeue(
        self,
    ) -> CrawlJob | None:

        if not self._jobs:
            return None

        return self._jobs.pop(0)

    async def size(
        self,
    ) -> int:
        return len(self._jobs)

    async def is_empty(
        self,
    ) -> bool:
        return len(self._jobs) == 0
