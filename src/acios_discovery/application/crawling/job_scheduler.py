from __future__ import annotations

from acios_discovery.domain.crawling import CrawlJob
from acios_discovery.domain.queue import JobQueue


class JobScheduler:
    """
    Schedules crawl jobs onto a queue.

    The scheduler knows nothing about
    crawling. Its responsibility is only
    to submit jobs to the configured queue.
    """

    def __init__(
        self,
        queue: JobQueue,
    ) -> None:
        self._queue = queue

    async def schedule(
        self,
        jobs: list[CrawlJob],
    ) -> None:

        for job in jobs:
            await self._queue.enqueue(job)
