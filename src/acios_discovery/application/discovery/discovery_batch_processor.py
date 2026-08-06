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
    It simply delegates each discovery to DiscoveryProcessor.
    """

    def __init__(
        self,
        processor: DiscoveryProcessor,
    ) -> None:
        self._processor = processor

    async def process(
        self,
        discoveries: list[RawDiscovery],
        *,
        starting_sequence: int = 1,
    ) -> list[Company]:

        companies: list[Company] = []

        sequence = starting_sequence

        for discovery in discoveries:

            company = await self._processor.process(
                sequence=sequence,
                discovery=discovery,
            )

            companies.append(company)

            sequence += 1

        return companies
