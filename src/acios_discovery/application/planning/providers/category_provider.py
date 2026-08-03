from __future__ import annotations

from acios_discovery.domain.taxonomy import (
    FINELIB_CATEGORY_MAP,
    Taxonomy,
)


class CategoryProvider:
    """
    Provides access to the Finelib taxonomy registry.
    """

    def categories(
        self,
    ) -> list[str]:
        return sorted(
            FINELIB_CATEGORY_MAP.keys()
        )

    def taxonomy(
        self,
        slug: str,
    ) -> Taxonomy:
        return FINELIB_CATEGORY_MAP[slug]

    def has_category(
        self,
        slug: str,
    ) -> bool:
        return slug in FINELIB_CATEGORY_MAP
