from __future__ import annotations

from acios_discovery.application.planning.models import (
    CrawlPlan,
    ListingUrl,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.domain.sources import Source

BASE = "https://www.finelib.com"


class ListingUrlBuilder:

    def __init__(
        self,
        taxonomy: CategoryProvider,
    ) -> None:

        self._taxonomy = taxonomy

    def build(
        self,
        plan: CrawlPlan,
    ) -> ListingUrl:

        taxonomy = self._taxonomy.taxonomy(
            plan.category_slug
        )

        city = plan.city.lower().replace(
            " ",
            "-"
        )

        if taxonomy.subcategory:

            url = (
                f"{BASE}/cities/"
                f"{city}/"
                f"{taxonomy.root}/"
                f"{taxonomy.category.lower().replace(' ','-')}/"
                f"{plan.category_slug}"
            )

        else:

            url = (
                f"{BASE}/cities/"
                f"{city}/"
                f"{plan.category_slug}"
            )

        if plan.page > 1:

            url += f"?page={plan.page}"

        return ListingUrl(
            source=Source.FINELIB,
            url=url,
            state=plan.state,
            city=plan.city,
            taxonomy_slug=plan.category_slug,
            page=plan.page,
        )
