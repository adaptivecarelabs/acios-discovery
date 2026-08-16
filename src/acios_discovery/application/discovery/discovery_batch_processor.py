from __future__ import annotations

from acios_discovery.application.discovery.discovery_processor import (
    DiscoveryProcessor,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.models import RawDiscovery


class DiscoveryBatchProcessor:
    """
    Processes a collection of discoveries.

    The processor itself contains no business rules.
    It delegates each discovery to DiscoveryProcessor.
    """

    def __init__(
        self,
        processor: DiscoveryProcessor,
    ) -> None:
        self._processor = processor

    async def process(
        self,
        discoveries: list[RawDiscovery],
    ) -> list[Company]:
        companies: list[Company] = []

        for discovery in discoveries:
            company = await self._processor.process(
                discovery=discovery,
            )

            companies.append(company)

        return companies
