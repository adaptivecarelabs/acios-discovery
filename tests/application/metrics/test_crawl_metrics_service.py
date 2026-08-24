from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)


def test_metrics_snapshot():

    service = CrawlMetricsService()

    service.record_job_processed()
    service.record_page()
    service.record_page()
    service.record_company(5)
    service.record_request()
    service.record_success()

    snapshot = service.snapshot()

    assert snapshot.jobs_processed == 1

    assert snapshot.pages_crawled == 2

    assert snapshot.companies_discovered == 5

    assert snapshot.requests_sent == 1

    assert snapshot.successful_requests == 1

    assert snapshot.duration_seconds > 0

    assert snapshot.pages_per_second > 0

    assert snapshot.companies_per_second > 0


def test_metrics_snapshot_tracks_duplicates_separately_from_companies():

    service = CrawlMetricsService()

    service.record_company(3)
    service.record_duplicate(2)

    snapshot = service.snapshot()

    assert snapshot.companies_discovered == 3
    assert snapshot.duplicates_found == 2


def test_metrics_snapshot_tracks_proxy_retries():

    service = CrawlMetricsService()

    service.record_proxy_retry()
    service.record_proxy_retry()
    service.record_proxy_retry(count=3)

    snapshot = service.snapshot()

    assert snapshot.proxy_retries == 5
