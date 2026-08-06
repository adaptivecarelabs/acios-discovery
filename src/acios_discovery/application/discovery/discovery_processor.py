from __future__ import annotations

from acios_discovery.application.company.discovery_company_registry_service import (
    DiscoveryCompanyRegistryService,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.models import RawDiscovery


class DiscoveryProcessor:
    """
    High-level application service responsible for processing a
    single RawDiscovery into the Company Registry.

    It delegates all registry logic to DiscoveryCompanyRegistryService.
    """

    def __init__(
        self,
        registry_service: DiscoveryCompanyRegistryService,
    ) -> None:
        self._registry_service = registry_service

    async def process(
        self,
        *,
        sequence: int,
        discovery: RawDiscovery,
    ) -> Company:
        """
        Register a discovery and return the resulting Company.
        """
        return await self._registry_service.register(
            sequence=sequence,
            discovery=discovery,
        )
