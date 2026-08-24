from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MetricsSnapshot:
    """
    Immutable metrics view.

    Safe to expose to dashboards,
    logs and monitoring.
    """

    jobs_processed: int

    pages_crawled: int

    companies_discovered: int

    duplicates_found: int

    proxy_retries: int

    requests_sent: int

    retries: int

    failures: int

    successful_requests: int

    http_failures: int

    duration_seconds: float

    pages_per_second: float

    companies_per_second: float
