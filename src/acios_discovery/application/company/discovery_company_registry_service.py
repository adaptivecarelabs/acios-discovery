from __future__ import annotations

from acios_discovery.application.company.company_factory import CompanyFactory
from acios_discovery.application.company.company_merge_service import CompanyMergeService
from acios_discovery.application.resolution.entity_resolution_service import (
    EntityResolutionService,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_repository import CompanyRepository
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.shared.logging import logger


class DiscoveryCompanyRegistryService:

    def __init__(
        self,
        repository: CompanyRepository,
        resolution_service: EntityResolutionService,
        factory: CompanyFactory,
        merge_service: CompanyMergeService,
    ) -> None:

        self._repository = repository
        self._resolution_service = resolution_service
        self._factory = factory
        self._merge_service = merge_service

    async def register(
        self,
        discovery: RawDiscovery,
    ) -> Company:


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

            company = self._merge_service.merge(
                resolution.company,
                discovery,
            )

            await self._repository.update(
                company,
            )

            return company

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

        await self._repository.add(
            company,
        )

        logger.info(
            "Registered %s",
            company.canonical_name,
        )

        return company
