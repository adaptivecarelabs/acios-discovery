from __future__ import annotations

from acios_discovery.application.discovery.discovery_processor import (
    DiscoveryProcessor,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.record import DiscoveryRecord


class DiscoveryBatchProcessor:
    """
    Processes a collection of discovery records.

    The processor itself contains no business rules.
    It delegates each record to DiscoveryProcessor.
    """

    def __init__(
        self,
        processor: DiscoveryProcessor,
    ) -> None:
        self._processor = processor

    async def process(
        self,
        records: list[DiscoveryRecord],
    ) -> list[Company]:
        companies: list[Company] = []

        for record in records:
            company = await self._processor.process(
                record=record,
            )

            companies.append(company)

        return companies
