from __future__ import annotations

from datetime import UTC
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from acios_discovery.application.discovery.discovery_persistence_service import (
    DiscoveryPersistenceService,
)
from acios_discovery.application.persistence.unit_of_work import (
    UnitOfWork,
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
from acios_discovery.domain.sources import (
    Source,
)


def make_record() -> DiscoveryRecord:
    return DiscoveryRecord(
        context=DiscoveryContext(
            source=Source.FINELIB,
            country="Nigeria",
            state="Lagos",
            city="Lagos",
            root="https://www.finelib.com",
            industry="Healthcare",
            sector="Health Services",
            category="Health",
            subcategory="Hospitals",
            listing_url=(
                "https://www.finelib.com/cities/lagos/health"
            ),
            page_number=1,
        ),
        company=RawDiscovery(
            source="finelib",
            business_name="Test Healthcare Company",
            detail_url=(
                "https://www.finelib.com/listing/"
                "test-healthcare-company/123456/"
            ),
            address="Lagos, Nigeria",
        ),
    )


class FakeUnitOfWork(UnitOfWork):
    def __init__(
        self,
        *,
        fail_on_outbox: bool = False,
    ) -> None:
        self.discovery_repository = Mock()
        self.discovery_repository.save = AsyncMock()

        self.outbox_repository = Mock()
        self.outbox_repository.add = AsyncMock(
            side_effect=(
                RuntimeError("outbox failure")
                if fail_on_outbox
                else None
            ),
        )

        self.commit_mock = AsyncMock()
        self.rollback_mock = AsyncMock()

    async def commit(self) -> None:
        await self.commit_mock()

    async def rollback(self) -> None:
        await self.rollback_mock()

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

@pytest.mark.asyncio
async def test_persist_saves_discovery_and_outbox_message() -> None:
    uow = FakeUnitOfWork()

    service = DiscoveryPersistenceService(
        unit_of_work=uow,
    )

    record = make_record()

    await service.persist(
        record,
    )

    uow.discovery_repository.save.assert_awaited_once_with(
        record,
    )

    uow.outbox_repository.add.assert_awaited_once()

    message = (
        uow.outbox_repository.add.await_args.args[0]
    )

    assert isinstance(message.id, UUID)
    assert message.event_type == "CompanyDiscoveredEvent"
    assert message.aggregate_type == "discovery"
    assert message.aggregate_id is None
    assert message.occurred_at.tzinfo == UTC
    assert message.created_at.tzinfo == UTC

    assert message.payload["record"]["company"]["business_name"] == (
        "Test Healthcare Company"
    )

    uow.commit_mock.assert_awaited_once()
    uow.rollback_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_persist_rolls_back_when_outbox_persistence_fails() -> None:
    uow = FakeUnitOfWork(
        fail_on_outbox=True,
    )

    service = DiscoveryPersistenceService(
        unit_of_work=uow,
    )

    record = make_record()

    with pytest.raises(
        RuntimeError,
        match="outbox failure",
    ):
        await service.persist(
            record,
        )

    uow.discovery_repository.save.assert_awaited_once_with(
        record,
    )

    uow.outbox_repository.add.assert_awaited_once()

    uow.commit_mock.assert_not_awaited()
    uow.rollback_mock.assert_awaited_once()
