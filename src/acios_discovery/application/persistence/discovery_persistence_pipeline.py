from __future__ import annotations

from acios_discovery.application.company.company_factory import CompanyFactory
from acios_discovery.application.resolution.entity_resolution_service import (
    EntityResolutionService,
)
from acios_discovery.domain.company.company_repository import (
    CompanyRepository,
)
from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.domain.discovery.repository import (
    DiscoveryRepository,
)


class DiscoveryPersistencePipeline:
    """
    Coordinates the complete persistence lifecycle
    of a discovered company.
    """

    def __init__(
        self,
        *,
        discovery_repository: DiscoveryRepository,
        company_repository: CompanyRepository,
        resolution_service: EntityResolutionService,
        company_factory: CompanyFactory,
    ) -> None:

        self._discovery_repository = discovery_repository

        self._company_repository = company_repository

        self._resolution_service = resolution_service

        self._company_factory = company_factory

    

    async def persist(
        self,
        *,
        sequence: int,
        discovery: DiscoveryRecord,
    ) -> None:
        """
        Persist a discovery and resolve it against
        existing canonical companies.
        """

        if await self._discovery_repository.exists(
            discovery,
        ):
            return

        await self._discovery_repository.save(
            discovery,
        )

        result = await self._resolution_service.resolve(
            discovery.company,
        )

        if not result.duplicate:
            company = await self._company_factory.create(
                discovery=discovery.company,
            )

            await self._company_repository.add(
                company,
            )
            return

        if result.company is None:
            raise RuntimeError(
                "Resolution marked discovery as duplicate "
                "but returned no company."
            )

        # Existing-company persistence will be added next.

        result.company.merge_discovery(
            discovery.company,
        )

        await self._company_repository.update(
            result.company,
        )
