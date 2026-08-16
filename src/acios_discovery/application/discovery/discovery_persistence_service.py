from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from acios_discovery.application.events.event_serializer import (
    serialize_event,
)
from acios_discovery.application.events.outbox import (
    OutboxMessage,
)
from acios_discovery.application.persistence.unit_of_work import (
    UnitOfWork,
)
from acios_discovery.domain.discovery.record import (
    DiscoveryRecord,
)
from acios_discovery.domain.events.company_discovered_event import (
    CompanyDiscoveredEvent,
)


class DiscoveryPersistenceService:
    """
    Persist a discovery and its corresponding domain event
    atomically through the UnitOfWork.

    The discovery record and outbox message are committed
    together. If either persistence operation fails, the
    UnitOfWork rolls the transaction back.
    """

    def __init__(
        self,
        *,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    async def persist(
        self,
        record: DiscoveryRecord,
    ) -> None:
        """
        Persist the discovery and record a CompanyDiscoveredEvent
        in the transactional outbox.

        The UnitOfWork owns the transaction boundary.
        """

        async with self._unit_of_work as uow:
            await uow.discovery_repository.save(
                record,
            )

            event = CompanyDiscoveredEvent(
                record=record,
            )

            message = OutboxMessage(
                id=uuid4(),
                event_type=type(event).__name__,
                aggregate_type="discovery",
                aggregate_id=None,
                payload=serialize_event(event),
                occurred_at=event.occurred_at,
                created_at=datetime.now(UTC),
            )

            await uow.outbox_repository.add(
                message,
            )
