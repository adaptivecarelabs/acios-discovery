from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from acios_discovery.bootstrap.discovery_services import (
    DiscoveryServices,
)
from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.infrastructure.persistence.orm.company_scalar_field_provenance import (
    CompanyScalarFieldProvenanceORM,
)
from acios_discovery.infrastructure.persistence.orm.company_set_field_provenance import (
    CompanySetFieldProvenanceORM,
)
from acios_discovery.infrastructure.persistence.orm.discovery import (
    DiscoveryORM,
)
from acios_discovery.infrastructure.persistence.orm.outbox_event import (
    OutboxEventORM,
)
from acios_discovery.infrastructure.persistence.repositories.company_repository import (
    SqlAlchemyCompanyRepository,
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
    detail_url = (
        "https://www.finelib.com/listing/"
        "Phytoscience-Double-Stem-Cell/101646/"
    )

    http = fixture_http_client(
        {
            (
                "https://www.finelib.com/cities/"
                "lagos/health"
            ): finelib_single_health_fixture,

            detail_url: finelib_detail_fixture,
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

    #
    # ---------- Execution statistics ----------
    #

    assert result.plans_generated > 0
    assert result.jobs_submitted > 0
    assert result.jobs_processed > 0
    assert result.pages_crawled > 0
    assert result.companies_discovered > 0
    assert result.workers == 1

    #
    # ---------- Discovery row: resolved, not PENDING ----------
    #

    discovery_stmt = select(DiscoveryORM).where(
        DiscoveryORM.detail_url == detail_url,
    )

    discovery_row = (
        await db_session.execute(discovery_stmt)
    ).scalar_one()

    assert discovery_row.resolution_status == "RESOLVED"
    assert discovery_row.resolved_company_id is not None
    assert discovery_row.resolved_at is not None

    #
    # ---------- Company row: created with merged detail data ----------
    #

    
    company_repository = SqlAlchemyCompanyRepository(db_session)

    company = await company_repository.get(
        CompanyId.parse(discovery_row.resolved_company_id),
    )

    assert company is not None

    assert company.canonical_name == (
        "PHYTOSCIENCE DOUBLE STEM CELL"
    )

    assert company.year_founded == 2012

    assert company.business_locations == 23

    assert company.employee_count == "20 and upwards"

    assert "natureregenerative@gmail.com" in company.emails

    assert "https://natureregenerative.com/" in company.websites

    # The listing card lists the same number twice among three
    # entries; set-field merging dedupes via phone_match, so
    # exactly two distinct numbers should be persisted.
    assert len(company.phone_numbers) == 2
    assert "0803 285 2530" in company.phone_numbers
    assert "0814 966 6894" in company.phone_numbers



    #
    # ---------- Field provenance: recorded at founding confidence ----------
    #

    scalar_provenance_stmt = select(
        CompanyScalarFieldProvenanceORM,
    ).where(
        CompanyScalarFieldProvenanceORM.company_id
        == company.id.value,
    )

    scalar_rows = (
        await db_session.execute(scalar_provenance_stmt)
    ).scalars().all()

    scalar_by_field = {
        row.field_name: row
        for row in scalar_rows
    }

    assert "year_founded" in scalar_by_field
    assert scalar_by_field["year_founded"].confidence == 100.0
    assert scalar_by_field["year_founded"].detail_url == detail_url

    set_provenance_stmt = select(
        CompanySetFieldProvenanceORM,
    ).where(
        CompanySetFieldProvenanceORM.company_id
        == company.id.value,
        CompanySetFieldProvenanceORM.field_name
        == "phone_numbers",
    )

    set_rows = (
        await db_session.execute(set_provenance_stmt)
    ).scalars().all()

    assert len(set_rows) == 2
    assert all(row.confidence == 100.0 for row in set_rows)

    #
    # ---------- Outbox: exactly one CompanyDiscoveredEvent ----------
    #
    # This is a first-time company creation, not a merge, so no
    # CompanyMergedEvent should be present.
    #

    discovered_count = await db_session.scalar(
        select(func.count()).select_from(OutboxEventORM).where(
            OutboxEventORM.event_type == "CompanyDiscoveredEvent",
        )
    )

    merged_count = await db_session.scalar(
        select(func.count()).select_from(OutboxEventORM).where(
            OutboxEventORM.event_type == "CompanyMergedEvent",
        )
    )

    assert discovered_count == 1
    assert merged_count == 0
