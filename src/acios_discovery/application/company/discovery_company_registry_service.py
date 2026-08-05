from __future__ import annotations

from acios_discovery.application.company.company_factory import CompanyFactory
from acios_discovery.application.company.company_merge_service import CompanyMergeService
from acios_discovery.application.resolution.entity_resolution_service import (
    EntityResolutionService,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_repository import CompanyRepository
from acios_discovery.domain.discovery.models import RawDiscovery


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
        sequence: int,
        discovery: RawDiscovery,
    ) -> Company:

        resolution = await self._resolution_service.resolve(
            discovery,
        )

        #
        # Existing Company
        #

        if resolution.company is not None:

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

        company = self._factory.create(
            sequence=sequence,
            discovery=discovery,
        )

        await self._repository.add(
            company,
        )

        return company
