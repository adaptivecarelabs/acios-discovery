from __future__ import annotations


class FinelibUrlSlugMapper:
    """
    Maps canonical taxonomy slugs to Finelib listing URL paths.

    The returned value is the complete category path relative to
    /cities/{city}/, not merely the final URL segment.

    Default behavior: {taxonomy_root}/{taxonomy_slug}, since most
    Finelib category paths nest under their root classification
    (e.g. root="business", slug="construction" -> "business/construction").
    Root-level categories with no nesting (root == slug, e.g.
    "agriculture") naturally collapse to just the slug via the
    special-case below.

    _OVERRIDES exists for the genuine exceptions: categories
    where Finelib's real URL segment doesn't match this pattern
    at all (a rename, like "healthcare" -> "health") or contains
    quirks the taxonomy has no way to encode (a stray leading
    hyphen in Finelib's own site, e.g. "business/-construction").
    These are discovered empirically through live crawling, not
    derivable from the taxonomy alone — there is no way to fully
    eliminate this list.

    Examples:
        healthcare -> health                    (override: rename)
        food       -> business/food              (root-based default)
        restaurants -> business/food/restaurants  (override: deeper nesting)
        agriculture -> agriculture                (root == slug)
        construction -> business/-construction    (override: site quirk)
    """

    _OVERRIDES: dict[str, str] = {
        "healthcare": "health",
        "food": "business/food",
        "restaurants": "business/food/restaurants",
        "construction": "business/-construction",
    }

    def listing_path(
        self,
        taxonomy_slug: str,
        *,
        root: str | None = None,
    ) -> str:

        if taxonomy_slug in self._OVERRIDES:
            return self._OVERRIDES[taxonomy_slug]

        if root is None or root == taxonomy_slug:
            return taxonomy_slug

        return f"{root}/{taxonomy_slug}"
