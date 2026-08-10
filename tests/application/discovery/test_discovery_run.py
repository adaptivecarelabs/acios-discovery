from acios_discovery.application.discovery.discovery_run import (
    DiscoveryRun,
    DiscoveryRunStatus,
)


def test_discovery_run_starts_created() -> None:
    run = DiscoveryRun(
        run_id="DISCOVERY-001",
    )

    assert run.run_id == "DISCOVERY-001"
    assert run.status == DiscoveryRunStatus.CREATED
    assert run.total_plans == 0
    assert run.total_jobs == 0
    assert run.error is None


def test_discovery_run_tracks_lifecycle() -> None:
    run = DiscoveryRun(
        run_id="DISCOVERY-001",
    )

    run.mark_planning(
        total_plans=3,
    )

    assert run.status == DiscoveryRunStatus.PLANNING
    assert run.total_plans == 3

    run.mark_queued(
        total_jobs=3,
    )

    assert run.status == DiscoveryRunStatus.QUEUED
    assert run.total_jobs == 3

    run.mark_crawling()

    assert run.status == DiscoveryRunStatus.CRAWLING

    run.mark_enriching()

    assert run.status == DiscoveryRunStatus.ENRICHING

    run.mark_processing()

    assert run.status == DiscoveryRunStatus.PROCESSING


def test_discovery_run_can_complete() -> None:
    run = DiscoveryRun(
        run_id="DISCOVERY-001",
    )

    run.mark_completed(
        completed_jobs=3,
        failed_jobs=0,
        discovered_records=25,
        enriched_records=20,
        registered_companies=18,
    )

    assert run.status == DiscoveryRunStatus.COMPLETED
    assert run.completed_jobs == 3
    assert run.failed_jobs == 0
    assert run.discovered_records == 25
    assert run.enriched_records == 20
    assert run.registered_companies == 18
    assert run.error is None


def test_discovery_run_can_fail() -> None:
    run = DiscoveryRun(
        run_id="DISCOVERY-001",
    )

    run.mark_failed(
        "Worker pool failed.",
    )

    assert run.status == DiscoveryRunStatus.FAILED
    assert run.error == "Worker pool failed."


def test_discovery_run_can_be_cancelled() -> None:
    run = DiscoveryRun(
        run_id="DISCOVERY-001",
    )

    run.mark_cancelled()

    assert run.status == DiscoveryRunStatus.CANCELLED
