import asyncio

from acios_discovery.application.discovery.service import (
    DiscoveryService,
)
from acios_discovery.application.enrichment.finelib_enricher import (
    FinelibEnricher,
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
from acios_discovery.infrastructure.http.httpx_client import (
    HttpxClient,
)
from acios_discovery.infrastructure.persistence.in_memory_discovery_repository import (
    InMemoryDiscoveryRepository,
)


async def main() -> None:

    #
    # Infrastructure
    #

    http = HttpxClient()

    connector = FinelibConnector(
        parser=FinelibParser(),
        mapper=FinelibMapper(),
    )

    enricher = FinelibEnricher(
        http=http,
        parser=FinelibDetailParser(),
        mapper=FinelibDetailMapper(),
    )

    repository = InMemoryDiscoveryRepository()

    #
    # Application
    #

    service = DiscoveryService(
        connector=connector,
        enricher=enricher,
        repository=repository,
        http=http,
    )

    #
    # Crawl Job
    #

    job = CrawlJob(
        source=Source.FINELIB,
        listing_url="https://www.finelib.com/cities/lagos/health",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    #
    # Execute
    #

    result = await service.run(job)

    print()
    print("=" * 80)
    print("DISCOVERY COMPLETED")
    print("=" * 80)
    print(f"Source      : {result.source}")
    print(f"Found       : {result.records_found}")
    print(f"Saved       : {result.records_saved}")
    print(f"Duplicates  : {result.duplicates}")

    if result.errors:
        print()
        print("Errors")
        print("-" * 80)

        for error in result.errors:
            print(error)

    print()
    print("=" * 80)
    print("DISCOVERED COMPANIES")
    print("=" * 80)

    records = await repository.list_all()

    for index, record in enumerate(records, start=1):

        company = record.company

        print(f"\n{index}. {company.business_name}")
        print(f"Address     : {company.address}")
        print(f"Phones      : {', '.join(company.phone_numbers)}")
        print(f"Email       : {company.email}")
        print(f"Website     : {company.website}")
        print(f"Founded     : {company.year_founded}")
        print(f"Employees   : {company.employee_count}")
        print(f"Locations   : {company.business_locations}")

        if company.product_types:
            print(
                f"Products    : {', '.join(company.product_types)}"
            )

        if company.payment_methods:
            print(
                f"Payments    : {', '.join(company.payment_methods)}"
            )

        if company.social_links:
            print("Socials")

            for platform, url in company.social_links.items():
                print(f"  {platform}: {url}")

        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())
