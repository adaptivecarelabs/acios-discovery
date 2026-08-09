from __future__ import annotations

from acios_discovery.domain.taxonomy import (
    FINELIB_CATEGORY_MAP,
    Taxonomy,
)


class CategoryProvider:
    """
    Provides access to the Finelib taxonomy registry.
    """

    def categories(self) -> list[str]:
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

    #
    # NEW
    #

    def first(self) -> str:
        """
        Returns the first registered category slug.
        """
        return self.categories()[0]

    def require(
        self,
        slug: str,
    ) -> str:
        """
        Validate that a category exists.

        Raises a descriptive error instead of KeyError.
        """

        if not self.has_category(
            slug,
        ):
            available = ", ".join(
                self.categories(),
            )

            raise ValueError(
                f"Unknown category '{slug}'. "
                f"Available categories: {available}"
            )

        return slug
