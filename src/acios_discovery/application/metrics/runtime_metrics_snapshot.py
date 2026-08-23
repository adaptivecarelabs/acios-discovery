from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeMetricsSnapshot:
    """
    Immutable snapshot representing the
    crawler runtime metrics at a point
    in time.
    """

    workers: int

    jobs_processed: int

    pages_crawled: int

    companies_discovered: int

    requests_sent: int

    retries: int

    failures: int

    successful_requests: int

    http_failures: int
