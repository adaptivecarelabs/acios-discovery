from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4
from acios_discovery.application.resolution.resolution_lock_keys import (
    build_resolution_lock_keys,
)
from acios_discovery.application.company.company_factory import CompanyFactory
from acios_discovery.application.company.company_merge_service import (
    CompanyMergeService,
)
from acios_discovery.application.events.event_serializer import (
    serialize_event,
)
from acios_discovery.application.events.outbox import OutboxMessage
from acios_discovery.application.persistence.unit_of_work import UnitOfWork
from acios_discovery.application.resolution.entity_resolution_service import (
    EntityResolutionService,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.events.company_merged_event import (
    CompanyMergedEvent,
)
from acios_discovery.shared.logging import logger


class DiscoveryCompanyRegistryService:
    """
    Resolves a discovery against the canonical company registry
    and atomically persists the outcome: the company write, the
    discovery's resolution state, and (on merge) a CompanyMergedEvent
    all commit together through a single UnitOfWork.
    """

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        resolution_service: EntityResolutionService,
        factory: CompanyFactory,
        merge_service: CompanyMergeService,
    ) -> None:

        self._unit_of_work = unit_of_work
        self._resolution_service = resolution_service
        self._factory = factory
        self._merge_service = merge_service

    async def register(
        self,
        record: DiscoveryRecord,
    ) -> Company:

        discovery = record.company

        async with self._unit_of_work as uow:

            #
            # Hold advisory locks on every identity signal this
            # discovery carries (name, phone, email, website)
            # for the rest of this transaction. This closes the
            # window between resolve() and the write below: two
            # concurrent discoveries that could match the same
            # company now serialize here instead of racing.
            #

            await uow.acquire_locks(
                build_resolution_lock_keys(discovery),
            )

            logger.info(
                "Checking company registry for %s",
                discovery.business_name,
            )

            resolution = await self._resolution_service.resolve(
                discovery,
            )

            #
            # Existing Company
            #

            if (
                resolution.company is not None
                and resolution.duplicate
            ):

                logger.info(
                    "Merging into existing company %s",
                    resolution.company.canonical_name,
                )

                summary = self._merge_service.merge(
                    resolution.company,
                    discovery,
                    confidence=resolution.confidence,
                )

                logger.info(
                    "Merged %s fields into %s: %s",
                    len(summary.changed_fields),
                    resolution.company.canonical_name,
                    summary.changed_fields,
                )

                await uow.company_repository.update(
                    resolution.company,
                )

                resolved_at = datetime.now(UTC)

                await uow.discovery_repository.resolve(
                    record,
                    resolution.company.id,
                    resolved_at,
                )

                event = CompanyMergedEvent(
                    company_id=resolution.company.id,
                    source=discovery.source,
                    detail_url=discovery.detail_url,
                    summary=summary,
                )

                message = OutboxMessage(
                    id=uuid4(),
                    event_type=type(event).__name__,
                    aggregate_type="company",
                    aggregate_id=str(resolution.company.id),
                    payload=serialize_event(event),
                    occurred_at=event.occurred_at,
                    created_at=datetime.now(UTC),
                )

                await uow.outbox_repository.add(
                    message,
                )

                return resolution.company

            #
            # New Company
            #

            logger.info(
                "Creating new company %s",
                discovery.business_name,
            )

            company = await self._factory.create(
                discovery=discovery,
            )

            logger.info(
                """
                COMPANY CREATED

                Emails: %s

                Websites: %s

                Phones: %s

                Socials: %s

                Products: %s
                """,
                company.emails,
                company.websites,
                company.phone_numbers,
                company.social_links,
                company.product_types,
            )

            await uow.company_repository.add(
                company,
            )

            resolved_at = datetime.now(UTC)

            await uow.discovery_repository.resolve(
                record,
                company.id,
                resolved_at,
            )

            logger.info(
                "Registered %s",
                company.canonical_name,
            )

            return company
