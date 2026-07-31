from acios_discovery.domain.queue.job_queue import JobQueue


def test_job_queue_is_abstract() -> None:
    assert JobQueue.__abstractmethods__
