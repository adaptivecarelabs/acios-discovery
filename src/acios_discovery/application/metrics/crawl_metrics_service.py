from __future__ import annotations

from datetime import UTC, datetime

from acios_discovery.application.metrics.runtime_metrics_snapshot import (
    RuntimeMetricsSnapshot,
)
from acios_discovery.domain.metrics.crawl_metrics import CrawlMetrics
from acios_discovery.domain.metrics.metrics_snapshot import MetricsSnapshot


class CrawlMetricsService:
    """
    Collects runtime metrics
    for an active crawl.
    """

    def __init__(self) -> None:

        self._metrics = CrawlMetrics()

    def record_job_processed(self) -> None:
        self._metrics.jobs_processed += 1

    def record_page(self) -> None:
        self._metrics.pages_crawled += 1

    def record_company(self, count: int = 1) -> None:
        self._metrics.companies_discovered += count

    def record_duplicate(self, count: int = 1) -> None:
        self._metrics.duplicates_found += count

    def record_proxy_retry(self, count: int = 1) -> None:
        self._metrics.proxy_retries += count

    def record_request(self) -> None:
        self._metrics.requests_sent += 1

    def record_retry(self) -> None:
        self._metrics.retries += 1

    def record_failure(self) -> None:
        self._metrics.failures += 1

    def record_success(self) -> None:
        self._metrics.successful_requests += 1

    def record_http_failure(self) -> None:
        self._metrics.http_failures += 1

    def finish(self) -> None:
        self._metrics.finished_at = datetime.now(UTC)

    def snapshot(self) -> MetricsSnapshot:

        end = (
            self._metrics.finished_at
            or datetime.now(UTC)
        )

        duration = (
            end - self._metrics.started_at
        ).total_seconds()

        if duration <= 0:
            duration = 0.000001

        return MetricsSnapshot(
            jobs_processed=self._metrics.jobs_processed,
            pages_crawled=self._metrics.pages_crawled,
            companies_discovered=self._metrics.companies_discovered,
            duplicates_found=self._metrics.duplicates_found,
            proxy_retries=self._metrics.proxy_retries,
            requests_sent=self._metrics.requests_sent,
            retries=self._metrics.retries,
            failures=self._metrics.failures,
            successful_requests=self._metrics.successful_requests,
            http_failures=self._metrics.http_failures,
            duration_seconds=duration,
            pages_per_second=(
                self._metrics.pages_crawled
                / duration
            ),
            companies_per_second=(
                self._metrics.companies_discovered
                / duration
            ),
        )


    def runtime_snapshot(
        self,
        *,
        workers: int,
    ) -> RuntimeMetricsSnapshot:

        snapshot = self.snapshot()

        return RuntimeMetricsSnapshot(
            workers=workers,
            jobs_processed=snapshot.jobs_processed,
            pages_crawled=snapshot.pages_crawled,
            companies_discovered=snapshot.companies_discovered,
            duplicates_found=snapshot.duplicates_found,
            proxy_retries=snapshot.proxy_retries,
            requests_sent=snapshot.requests_sent,
            retries=snapshot.retries,
            failures=snapshot.failures,
            successful_requests=snapshot.successful_requests,
            http_failures=snapshot.http_failures,
        )

    