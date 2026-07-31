from abc import ABC, abstractmethod

from acios_discovery.domain.crawling.job import CrawlJob


class JobQueue(ABC):
    """
    Abstract queue for crawl jobs.

    Different implementations may use
    memory, Redis, RabbitMQ, Kafka,
    SQS, etc.
    """

    @abstractmethod
    async def enqueue(
        self,
        job: CrawlJob,
    ) -> None:
        """
        Add a job to the queue.
        """
        ...

    @abstractmethod
    async def dequeue(
        self,
    ) -> CrawlJob | None:
        """
        Retrieve the next job.

        Returns None when the queue
        is empty.
        """
        ...

    @abstractmethod
    async def size(
        self,
    ) -> int:
        """
        Number of pending jobs.
        """
        ...

    @abstractmethod
    async def is_empty(
        self,
    ) -> bool:
        """
        Whether there are any jobs.
        """
        ...
