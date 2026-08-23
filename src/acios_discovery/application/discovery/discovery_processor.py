from __future__ import annotations

from acios_discovery.application.company.discovery_company_registry_service import (
    DiscoveryCompanyRegistryService,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.record import DiscoveryRecord
from acios_discovery.shared.logging import logger


class DiscoveryProcessor:
    """
    High-level application service responsible for processing
    a single DiscoveryRecord into the Company Registry.

    It delegates all registry logic to
    DiscoveryCompanyRegistryService.
    """

    def __init__(
        self,
        registry_service: DiscoveryCompanyRegistryService,
    ) -> None:
        self._registry_service = registry_service

    async def process(
        self,
        *,
        record: DiscoveryRecord,
    ) -> Company:
        """
        Register a discovery record and return the resulting Company.
        """

        discovery = record.company

        logger.info(
            "Processing discovery %s",
            discovery.business_name,
        )

        company = await self._registry_service.register(
            record=record,
        )

        logger.info(
            """
            EMAIL : %s
            WEBSITE : %s
            SOCIALS : %s
            PRODUCTS : %s
            PAYMENTS : %s
            """,
            discovery.email,
            discovery.website,
            discovery.social_links,
            discovery.product_types,
            discovery.payment_methods,
        )

        logger.info(
            "Company available in registry: %s",
            company.canonical_name,
        )

        return company
