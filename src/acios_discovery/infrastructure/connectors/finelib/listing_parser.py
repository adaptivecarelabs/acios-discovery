from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.infrastructure.connectors.base import (
    BaseDirectoryParser,
)


class FinelibParser(BaseDirectoryParser):
    """Parser for Finelib category pages."""

    def find_business_cards(
        self,
        html: str,
    ) -> list[Tag]:
        """
        Return every business listing node.
        """

        soup = BeautifulSoup(
            html,
            "lxml",
        )

        cards = soup.select(
            "div.box-682.bg-none",
        )

        return list(cards)

    def parse(
        self,
        html: str,
    ) -> list[RawDiscovery]:
        raise NotImplementedError

    def is_fallback_page(
        self,
        html: str,
    ) -> bool:
        """
        Detect Finelib's generic nationwide fallback listing.

        Finelib returns HTTP 200 with a generic "Nigeria {X}"
        page for any (city, category) URL that does not have a
        dedicated listing, rather than a 404. This page is
        indistinguishable from a real listing by status code —
        it must be detected by content. Confirmed empirically:
        a real listing page's <h1> starts with the requested
        city's name (e.g. "Lagos Healthcare Service Centres",
        "Lagos Restaurants and Eateries"); the fallback page's
        <h1> always starts with the literal word "Nigeria"
        (e.g. "Nigeria Health Sectors", "Nigeria Restaurants").
        """

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        h1 = soup.find("h1")

        if h1 is None:
            return False

        text = h1.get_text(strip=True)

        return text.startswith("Nigeria ")

    def next_page_url(
        self,
        html: str,
        current_url: str,
    ) -> str | None:
        """
        Return the absolute URL of the next Finelib
        listing page.

        Returns None when the current page is the
        last page.
        """

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        paging = soup.find(
            "div",
            class_="paging-box",
        )

        if not isinstance(
            paging,
            Tag,
        ):
            return None

        for link in paging.find_all("a"):

            text = link.get_text(
                strip=True,
            )

            if text != "Next":
                continue

            href = link.get("href")

            if not isinstance(
                href,
                str,
            ):
                return None

            return urljoin(
                current_url,
                href,
            )

        return None
