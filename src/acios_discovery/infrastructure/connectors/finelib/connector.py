
from acios_discovery.domain.connectors import BaseConnector
from acios_discovery.domain.discovery import (
    DiscoveryContext,
    DiscoveryRecord,
    RawDiscovery,
)
from acios_discovery.domain.sources import Source
from acios_discovery.domain.taxonomy import FINELIB_CATEGORY_MAP

from .mapper import FinelibMapper
from .parser import FinelibParser


class FinelibConnector(BaseConnector):
    """
    Orchestrates the parsing of a Finelib listing page
    into DiscoveryRecord objects.

    This connector performs no HTTP requests.
    HTML is injected by the caller.
    """

    def __init__(
        self,
        parser: FinelibParser,
        mapper: FinelibMapper,
    ) -> None:
        self._parser = parser
        self._mapper = mapper

    async def crawl(self) -> list[DiscoveryRecord]:
        raise NotImplementedError(
            "Use crawl_listing() instead."
        )

    async def crawl_listing(
        self,
        *,
        html: str,
        listing_url: str,
        state: str,
        city: str,
        category_slug: str,
    ) -> list[DiscoveryRecord]:

        taxonomy = FINELIB_CATEGORY_MAP[
            category_slug
        ]

        cards = self._parser.find_business_cards(
            html,
        )

        discoveries: list[
            DiscoveryRecord
        ] = []

        for card in cards:

            company = RawDiscovery(
                source=Source.FINELIB,
                business_name=self._mapper.extract_business_name(
                    card
                ),
                detail_url=self._mapper.extract_detail_url(
                    card
                ),
                address=self._mapper.extract_address(
                    card
                ),
                phone_numbers=self._mapper.extract_phone_numbers(
                    card
                ),
                description=self._mapper.extract_description(
                    card
                ),
            )

            context = DiscoveryContext(
                source=Source.FINELIB,
                state=state,
                city=city,
                industry=taxonomy.industry,
                sector=taxonomy.sector,
                category=taxonomy.category,
                subcategory=taxonomy.subcategory,
                listing_url=listing_url,
            )

            discoveries.append(
                DiscoveryRecord(
                    company=company,
                    context=context,
                )
            )

        return discoveries
