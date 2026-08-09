from acios_discovery.domain.connectors.base import (
    BaseConnector,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.discovery import (
    DiscoveryContext,
    DiscoveryRecord,
)
from acios_discovery.domain.sources import Source
from acios_discovery.domain.taxonomy import FINELIB_CATEGORY_MAP

from .listing_mapper import FinelibMapper
from .listing_parser import FinelibParser


class FinelibConnector(BaseConnector):
    """
    Parses Finelib listing pages into DiscoveryRecord objects.

    This connector is responsible ONLY for discovering
    businesses from listing pages.

    It does NOT enrich businesses from their detail pages.
    """

    @property
    def source(self) -> Source:
        return Source.FINELIB

    def __init__(
        self,
        parser: FinelibParser,
        mapper: FinelibMapper,
    ) -> None:

        self._parser = parser
        self._mapper = mapper

    async def crawl(
        self,
        job: CrawlJob,
    ) -> list[DiscoveryRecord]:
        raise NotImplementedError(
            "The application worker is responsible "
            "for downloading listing pages."
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

            company = self._mapper.map(
                card,
            )

            context = DiscoveryContext(
                source=Source.FINELIB,
                state=state,
                city=city,
                root=taxonomy.root,
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

    def next_page_url(
        self,
        html: str,
        current_url: str,
    ) -> str | None:
        """
        Return the absolute URL of the next
        Finelib listing page.

        Returns None when there is no next page.
        """

        return self._parser.next_page_url(
            html=html,
            current_url=current_url,
        )
