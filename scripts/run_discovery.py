import asyncio

from acios_discovery.application.discovery.service import (
    DiscoveryService,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)
from acios_discovery.infrastructure.connectors.finelib.detail_mapper import (
    FinelibDetailMapper,
)
from acios_discovery.infrastructure.connectors.finelib.detail_parser import (
    FinelibDetailParser,
)
from acios_discovery.infrastructure.connectors.finelib.listing_mapper import (
    FinelibMapper,
)
from acios_discovery.infrastructure.connectors.finelib.listing_parser import (
    FinelibParser,
)
from acios_discovery.infrastructure.enrichment.finelib.enricher import (
    FinelibEnricher,
)
from acios_discovery.infrastructure.http.httpx_client import (
    HttpxClient,
)
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)


async def main():

    http = HttpxClient()

    service = DiscoveryService(
        connector=FinelibConnector(
            parser=FinelibParser(),
            mapper=FinelibMapper(),
        ),
        enricher=FinelibEnricher(
            parser=FinelibDetailParser(),
            mapper=FinelibDetailMapper(),
        ),
        repository=InMemoryDiscoveryRepository(),
        http=http,
    )

    result = await service.run(
        CrawlJob(
            source=Source.FINELIB,
            listing_url="https://www.finelib.com/cities/lagos/health",
            state="Lagos",
            city="Lagos",
            category_slug="health",
        )
    )

    print()
    print("=" * 80)
    print(result)
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
