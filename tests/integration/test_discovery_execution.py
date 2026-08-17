from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from acios_discovery.bootstrap.discovery_services import (
    DiscoveryServices,
)


class SinglePlanGenerator:
    """
    Deterministic planner used by the execution E2E test.

    Produces exactly one known Finelib plan.
    """

    def generate(
        self,
        *,
        state: str,
    ):
        from acios_discovery.application.planning.models import (
            CrawlPlan,
        )

        return [
            CrawlPlan(
                state=state,
                city="Lagos",
                category_slug="healthcare",
            )
        ]

    


@pytest.mark.asyncio
async def test_discovery_execution_runs_complete_pipeline(
    db_session: AsyncSession,
    fixture_http_client,
    finelib_single_health_fixture: str,
    finelib_detail_fixture: str,
    test_session_factory,
) -> None:
    http = fixture_http_client(
        {
            (
                "https://www.finelib.com/cities/"
                "lagos/health"
            ): finelib_single_health_fixture,

            (
                "https://www.finelib.com/listing/"
                "Phytoscience-Double-Stem-Cell/101646/"
            ): finelib_detail_fixture,
        }
    )

    services = DiscoveryServices(
        session=db_session,
        workers=1,
        http=http,
        planner=SinglePlanGenerator(),
        session_factory=test_session_factory,
    )

    result = await services.execution_service.run(
        state="Lagos",
    )

    assert result.plans_generated > 0
    assert result.jobs_submitted > 0
    assert result.jobs_processed > 0
    assert result.pages_crawled > 0
    assert result.companies_discovered > 0
    assert result.workers == 1
