from __future__ import annotations

from acios_discovery.application.planning.models import (
    CrawlPlan,
    ListingUrl,
)
from acios_discovery.application.planning.providers.category_provider import (
    CategoryProvider,
)
from acios_discovery.domain.sources import Source
from acios_discovery.infrastructure.connectors.finelib.url_slug_mapper import (
    FinelibUrlSlugMapper,
)

BASE = "https://www.finelib.com"


class ListingUrlBuilder:
    """
    Builds canonical Finelib listing URLs.

    Taxonomy metadata describes the business classification.
    FinelibUrlSlugMapper describes how that classification is represented
    in Finelib's URL structure.
    """

    def __init__(
        self,
        taxonomy: CategoryProvider,
        slug_mapper: FinelibUrlSlugMapper,
    ) -> None:
        self._taxonomy = taxonomy
        self._slug_mapper = slug_mapper

    def build(
        self,
        plan: CrawlPlan,
    ) -> ListingUrl:
        self._taxonomy.require(
            plan.category_slug,
        )

        taxonomy = self._taxonomy.taxonomy(
            plan.category_slug,
        )

        path = self._slug_mapper.listing_path(
            plan.category_slug,
            root=taxonomy.root,
        )

        city = plan.city.strip().lower().replace(
            " ",
            "-",
        )

        url = (
            f"{BASE}/cities/"
            f"{city}/"
            f"{path}"
        )

        if plan.page > 1:
            url += f"/page-{plan.page}"

        return ListingUrl(
            source=Source.FINELIB,
            url=url,
            state=plan.state,
            city=plan.city,
            taxonomy_slug=plan.category_slug,
            page=plan.page,
        )
