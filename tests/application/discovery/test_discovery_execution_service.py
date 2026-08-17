from acios_discovery.application.discovery.discovery_execution_service import (
    DiscoveryExecutionService,
)


class FakePlanner:
    def generate(
        self,
        *,
        state: str,
    ):
        return [
            object(),
            object(),
            object(),
        ]


class FakeSubmissionService:
    async def submit(
        self,
        plans,
    ) -> int:
        assert len(plans) == 3
        return 3


class FakeSupervisor:
    async def run(self):
        return type(
            "SupervisorResult",
            (),
            {
                "workers": 4,
                "jobs_processed": 3,
                "pages_crawled": 7,
                "companies_discovered": 42,
            },
        )()


async def test_execution_service_coordinates_discovery() -> None:
    service = DiscoveryExecutionService(
        planner=FakePlanner(),
        job_submission_service=FakeSubmissionService(),
        crawl_supervisor=FakeSupervisor(),
    )

    result = await service.run(
        state="Lagos",
    )

    assert result.plans_generated == 3
    assert result.jobs_submitted == 3
    assert result.jobs_processed == 3
    assert result.pages_crawled == 7
    assert result.companies_discovered == 42
    assert result.workers == 4
