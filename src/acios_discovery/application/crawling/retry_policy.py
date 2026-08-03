from __future__ import annotations

from acios_discovery.domain.crawling import (
    CrawlJob,
)


class RetryPolicy:
    """
    Determines whether a crawl job
    should be retried.
    """

    def should_retry(
        self,
        job: CrawlJob,
    ) -> bool:

        return job.retries < job.max_retries
