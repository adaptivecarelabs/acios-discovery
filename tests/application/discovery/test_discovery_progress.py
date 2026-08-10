from acios_discovery.application.discovery.discovery_progress import (
    DiscoveryProgress,
)


def test_progress_reports_finished_jobs() -> None:
    progress = DiscoveryProgress(
        total_jobs=10,
        completed_jobs=6,
        failed_jobs=2,
    )

    assert progress.finished_jobs == 8


def test_progress_reports_remaining_jobs() -> None:
    progress = DiscoveryProgress(
        total_jobs=10,
        completed_jobs=6,
        failed_jobs=2,
    )

    assert progress.remaining_jobs == 2


def test_progress_is_complete_when_all_jobs_finish() -> None:
    progress = DiscoveryProgress(
        total_jobs=10,
        completed_jobs=8,
        failed_jobs=2,
    )

    assert progress.is_complete is True


def test_progress_is_not_complete_when_jobs_remain() -> None:
    progress = DiscoveryProgress(
        total_jobs=10,
        completed_jobs=7,
        failed_jobs=2,
    )

    assert progress.is_complete is False
