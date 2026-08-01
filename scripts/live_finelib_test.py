import asyncio
from pprint import pprint

from acios_discovery.domain.discovery.discovery import Discovery
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


async def main() -> None:

    http = HttpxClient()

    connector = FinelibConnector(
        parser=FinelibParser(),
        mapper=FinelibMapper(),
    )

    detail_parser = FinelibDetailParser()
    detail_mapper = FinelibDetailMapper()

    print("\nDownloading listing page...\n")

    listing_html = await http.get(
        "https://www.finelib.com/cities/lagos/health"
    )

    records = await connector.crawl_listing(
        html=listing_html,
        listing_url="https://www.finelib.com/cities/lagos/health",
        state="Lagos",
        city="Lagos",
        category_slug="health",
    )

    print(f"Found {len(records)} businesses.\n")

    #
    # Only enrich the first business.
    #

    record = records[0]

    company = record.company

    print("=" * 80)
    print("LISTING DATA")
    print("=" * 80)

    pprint(company)

    if not company.detail_url:
        print("\nNo detail page found.")
        return

    print("\nDownloading detail page...\n")

    detail_html = await http.get(
        company.detail_url,
    )

    with open("detail.html", "w", encoding="utf-8") as f:
        f.write(detail_html)

    soup = detail_parser.parse(
        detail_html,
    )

    discovery = Discovery(
        business_name=company.business_name,
        detail_url=company.detail_url,
        address=company.address,
        description=company.description,
        phone_numbers=list(company.phone_numbers),
    )

    discovery = detail_mapper.enrich(
        discovery,
        soup,
    )

    print()
    print("=" * 80)
    print("ENRICHED DATA")
    print("=" * 80)

    pprint(discovery)


if __name__ == "__main__":
    asyncio.run(main())
