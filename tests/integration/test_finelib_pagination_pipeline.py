from __future__ import annotations

from collections.abc import Mapping

import pytest

from acios_discovery.application.discovery.service import (
    DiscoveryService,
)
from acios_discovery.domain.crawling.job import (
    CrawlJob,
)
from acios_discovery.infrastructure.connectors.finelib.connector import (
    FinelibConnector,
)
from acios_discovery.infrastructure.connectors.finelib.listing_mapper import (
    FinelibMapper,
)
from acios_discovery.infrastructure.connectors.finelib.listing_parser import (
    FinelibParser,
)
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)


class PassthroughEnricher:
    """
    Used for pagination integration tests.

    Returns the discovered record unchanged.
    """

    async def enrich(self, record):
        return record



class FixtureHttpClient:
    """
    Fake HTTP client backed by real HTML fixtures.

    It records every requested URL so the test can verify
    exactly which listing pages were downloaded.
    """

    def __init__(
        self,
        pages: Mapping[str, str],
    ) -> None:

        self._pages = dict(pages)

        self.requests: list[str] = []

    async def get(
        self,
        url: str,
    ) -> str:

        self.requests.append(
            url,
        )

        return self._pages[url]


@pytest.mark.asyncio
async def test_real_connector_crawls_multiple_pages(
    lagos_agriculture_service_page1,
    lagos_agriculture_service_page2,
):

    repository = InMemoryDiscoveryRepository()

    connector = FinelibConnector(
        parser=FinelibParser(),
        mapper=FinelibMapper(),
    )

    http = FixtureHttpClient(
        {
            "https://www.finelib.com/cities/lagos/agriculture": (
                lagos_agriculture_service_page1
            ),
            "https://www.finelib.com/cities/lagos/agriculture/page-2": (
                lagos_agriculture_service_page2
            ),
        }
    )

    service = DiscoveryService(
        connector=connector,
        enricher=PassthroughEnricher(),
        repository=repository,
        http=http,
    )

    job = CrawlJob(
        source="finelib",
        listing_url="https://www.finelib.com/cities/lagos/agriculture",
        state="Lagos",
        city="Lagos",
        category_slug="food",
    )

    result = await service.run(job)

    assert result.records_found > 0

    assert result.records_saved == result.records_found

    assert await repository.count() == result.records_saved

    assert http.requests == [
        "https://www.finelib.com/cities/lagos/agriculture",
        "https://www.finelib.com/cities/lagos/agriculture/page-2",
    ]
