import pytest

from acios_discovery.application.company.company_factory import (
    CompanyFactory,
)
from acios_discovery.application.company.company_merge_service import (
    CompanyMergeService,
)
from acios_discovery.application.company.discovery_company_registry_service import (
    DiscoveryCompanyRegistryService,
)
from acios_discovery.application.company.sequential_company_id_allocator import (
    SequentialCompanyIdAllocator,
)
from acios_discovery.application.metrics.crawl_metrics_service import (
    CrawlMetricsService,
)
from acios_discovery.application.persistence.unit_of_work import (
    UnitOfWork,
)
from acios_discovery.application.resolution.entity_resolution_engine import (
    EntityResolutionEngine,
)
from acios_discovery.application.resolution.entity_resolution_service import (
    EntityResolutionService,
)
from acios_discovery.domain.discovery.context import (
    DiscoveryContext,
)
from acios_discovery.domain.discovery.models import (
    RawDiscovery,
)
from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)
from acios_discovery.infrastructure.repositories.in_memory_company_match_repository import (
    InMemoryCompanyMatchRepository,
)
from acios_discovery.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)


def make_context() -> DiscoveryContext:
    return DiscoveryContext(
        source=Source.FINELIB,
        state="Lagos",
        city="Lagos",
        category="Health",
        listing_url="https://www.finelib.com/cities/lagos/health",
    )


def make_record(
    name: str,
    detail_url: str,
    phone: str | None = None,
) -> DiscoveryRecord:

    return DiscoveryRecord(
        context=make_context(),
        company=RawDiscovery(
            source=Source.FINELIB,
            business_name=name,
            detail_url=detail_url,
            phone_numbers=[phone] if phone else [],
        ),
    )


class FakeUnitOfWork(UnitOfWork):
    def __init__(
        self,
        *,
        company_repository: InMemoryCompanyRepository,
        discovery_repository: InMemoryDiscoveryRepository,
    ) -> None:

        self.company_repository = company_repository
        self.discovery_repository = discovery_repository

        from unittest.mock import AsyncMock, Mock

        self.outbox_repository = Mock()
        self.outbox_repository.add = AsyncMock()

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()


@pytest.mark.asyncio
async def test_register_creates_company():

    company_repository = InMemoryCompanyRepository()
    discovery_repository = InMemoryDiscoveryRepository()

    record = make_record(
        "Drugstoc",
        detail_url="https://www.finelib.com/listing/drugstoc/1/",
    )

    await discovery_repository.save(record)

    uow = FakeUnitOfWork(
        company_repository=company_repository,
        discovery_repository=discovery_repository,
    )

    resolution = EntityResolutionService(
        repository=InMemoryCompanyMatchRepository(company_repository),
        engine=EntityResolutionEngine(),
    )

    service = DiscoveryCompanyRegistryService(
        unit_of_work=uow,
        resolution_service=resolution,
        factory=CompanyFactory(id_allocator=SequentialCompanyIdAllocator()),
        merge_service=CompanyMergeService(),
    )

    company = await service.register(
        record=record,
    )

    assert company.canonical_name == "DRUGSTOC"

    assert await company_repository.count() == 1

    # register() resolves the discovery; it would have raised
    # ValueError above if resolve() had not been called, since
    # the record was pre-saved but not pre-resolved.

    uow.outbox_repository.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_merges_duplicate():

    company_repository = InMemoryCompanyRepository()
    discovery_repository = InMemoryDiscoveryRepository()

    factory = CompanyFactory(id_allocator=SequentialCompanyIdAllocator())

    existing = await factory.create(
        discovery=RawDiscovery(
            source=Source.FINELIB,
            business_name="Drugstoc",
            phone_numbers=["08030000000"],
        ),
    )

    await company_repository.add(existing)

    record = make_record(
        "Drugstoc Ltd",
        detail_url="https://www.finelib.com/listing/drugstoc-ltd/2/",
        phone="08030000000",
    )

    await discovery_repository.save(record)

    uow = FakeUnitOfWork(
        company_repository=company_repository,
        discovery_repository=discovery_repository,
    )

    resolution = EntityResolutionService(
        repository=InMemoryCompanyMatchRepository(company_repository),
        engine=EntityResolutionEngine(),
    )

    service = DiscoveryCompanyRegistryService(
        unit_of_work=uow,
        resolution_service=resolution,
        factory=CompanyFactory(id_allocator=SequentialCompanyIdAllocator()),
        merge_service=CompanyMergeService(),
    )

    company = await service.register(
        record=record,
    )

    assert company.id == existing.id

    assert any(
        alias.upper() == "DRUGSTOC LTD"
        for alias in company.aliases
    )

    assert "08030000000" in company.phone_numbers

    uow.outbox_repository.add.assert_awaited_once()

    message = uow.outbox_repository.add.await_args.args[0]

    assert message.event_type == "CompanyMergedEvent"
    assert message.aggregate_type == "company"
    assert message.aggregate_id == str(existing.id)


@pytest.mark.asyncio
async def test_register_records_duplicate_metric_on_merge():
    """
    Regression test: a merge must increment the metrics
    service's duplicate counter synchronously, at the point the
    merge decision is made — not via the outbox/event relay,
    which is a separate, asynchronous, out-of-process delivery
    path that a live crawl run's own metrics snapshot cannot
    observe.
    """

    company_repository = InMemoryCompanyRepository()
    discovery_repository = InMemoryDiscoveryRepository()

    factory = CompanyFactory(id_allocator=SequentialCompanyIdAllocator())

    existing = await factory.create(
        discovery=RawDiscovery(
            source=Source.FINELIB,
            business_name="Drugstoc",
            phone_numbers=["08030000000"],
        ),
    )

    await company_repository.add(existing)

    record = make_record(
        "Drugstoc Ltd",
        detail_url="https://www.finelib.com/listing/drugstoc-ltd/metrics/",
        phone="08030000000",
    )

    await discovery_repository.save(record)

    uow = FakeUnitOfWork(
        company_repository=company_repository,
        discovery_repository=discovery_repository,
    )

    resolution = EntityResolutionService(
        repository=InMemoryCompanyMatchRepository(company_repository),
        engine=EntityResolutionEngine(),
    )

    metrics = CrawlMetricsService()

    service = DiscoveryCompanyRegistryService(
        unit_of_work=uow,
        resolution_service=resolution,
        factory=CompanyFactory(id_allocator=SequentialCompanyIdAllocator()),
        merge_service=CompanyMergeService(),
        metrics=metrics,
    )

    await service.register(
        record=record,
    )

    assert metrics.snapshot().duplicates_found == 1


@pytest.mark.asyncio
async def test_register_does_not_record_duplicate_metric_on_create():
    """
    A brand-new company (no existing match) must NOT increment
    the duplicate counter.
    """

    company_repository = InMemoryCompanyRepository()
    discovery_repository = InMemoryDiscoveryRepository()

    record = make_record(
        "A Genuinely New Company",
        detail_url="https://www.finelib.com/listing/new-co/metrics/",
    )

    await discovery_repository.save(record)

    uow = FakeUnitOfWork(
        company_repository=company_repository,
        discovery_repository=discovery_repository,
    )

    resolution = EntityResolutionService(
        repository=InMemoryCompanyMatchRepository(company_repository),
        engine=EntityResolutionEngine(),
    )

    metrics = CrawlMetricsService()

    service = DiscoveryCompanyRegistryService(
        unit_of_work=uow,
        resolution_service=resolution,
        factory=CompanyFactory(id_allocator=SequentialCompanyIdAllocator()),
        merge_service=CompanyMergeService(),
        metrics=metrics,
    )

    await service.register(
        record=record,
    )

    assert metrics.snapshot().duplicates_found == 0


@pytest.mark.asyncio
async def test_register_works_without_metrics_service():
    """
    metrics is optional — register() must not raise when no
    metrics service is provided (matches every call site prior
    to this feature, and any future caller that doesn't care
    about metrics).
    """

    company_repository = InMemoryCompanyRepository()
    discovery_repository = InMemoryDiscoveryRepository()

    factory = CompanyFactory(id_allocator=SequentialCompanyIdAllocator())

    existing = await factory.create(
        discovery=RawDiscovery(
            source=Source.FINELIB,
            business_name="Drugstoc",
            phone_numbers=["08030000000"],
        ),
    )

    await company_repository.add(existing)

    record = make_record(
        "Drugstoc Ltd",
        detail_url="https://www.finelib.com/listing/drugstoc-ltd/no-metrics/",
        phone="08030000000",
    )

    await discovery_repository.save(record)

    uow = FakeUnitOfWork(
        company_repository=company_repository,
        discovery_repository=discovery_repository,
    )

    resolution = EntityResolutionService(
        repository=InMemoryCompanyMatchRepository(company_repository),
        engine=EntityResolutionEngine(),
    )

    service = DiscoveryCompanyRegistryService(
        unit_of_work=uow,
        resolution_service=resolution,
        factory=CompanyFactory(id_allocator=SequentialCompanyIdAllocator()),
        merge_service=CompanyMergeService(),
        # metrics intentionally omitted
    )

    company = await service.register(
        record=record,
    )

    assert company.id == existing.id
