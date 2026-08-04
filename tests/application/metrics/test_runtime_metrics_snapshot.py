from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)


def test_runtime_snapshot():

    metrics = CrawlMetricsService()

    metrics.record_job_processed()
    metrics.record_page()
    metrics.record_company(5)

    snapshot = metrics.runtime_snapshot(
        workers=4,
    )

    assert snapshot.workers == 4
    assert snapshot.jobs_processed == 1
    assert snapshot.pages_crawled == 1
    assert snapshot.companies_discovered == 5
