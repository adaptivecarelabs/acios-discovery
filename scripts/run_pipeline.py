from __future__ import annotations

import asyncio
import time

from acios_discovery.application.planning.models.crawl_plan import CrawlPlan
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.bootstrap.discovery_pipeline import build_pipeline
from acios_discovery.shared.logging import configure_logging


async def main() -> None:

    configure_logging()

    print()
    print("=" * 80)
    print("ACIOS Discovery Pipeline")
    print("=" * 80)

    #
    # Load taxonomy
    #

    category_provider = CategoryProvider()

    print()
    print("Available Categories")
    print("-" * 80)

    for slug in category_provider.categories():
        print(f"• {slug}")

    #
    # Validate category
    #

    category_slug = category_provider.require(
        "food",
    )

    #
    # Build pipeline
    #

    pipeline = build_pipeline()

    #
    # Build crawl plan
    #

    plan = CrawlPlan(
        state="Lagos",
        city="Lagos",
        category_slug=category_slug,
        page=1,
    )

    started = time.perf_counter()

    result = await pipeline.execute(
        plan,
    )

    records = await pipeline._crawler._repository.list_all()

    print()
    print("=" * 80)
    print("ENRICHED RECORDS")
    print("=" * 80)

    for record in records:

        c = record.company

        print()

        print(c.business_name)

        print("Phone:", c.phone_numbers)

        print("Website:", c.website)

        print("Email:", c.email)

        print("Social:", c.social_links)

        print("Founded:", c.year_founded)

        print("Employees:", c.employee_count)

        print("Products:", c.product_types)

    elapsed = time.perf_counter() - started

    print()
    print("=" * 80)
    print("DISCOVERY SUMMARY")
    print("=" * 80)

    print(f"Source              : {result.source}")
    print(f"Companies Found     : {result.records_found}")
    print(f"Companies Saved     : {result.records_saved}")
    print(f"Duplicates          : {result.duplicates}")
    print(f"Duration            : {elapsed:.2f} seconds")

    if result.errors:

        print()
        print("Errors")
        print("-" * 80)

        for error in result.errors:
            print(error)

    print()
    print("=" * 80)
    print("Pipeline completed.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
