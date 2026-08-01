from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.infrastructure.connectors.base import (
    BaseDirectoryParser,
)


class FinelibParser(BaseDirectoryParser):
    """Parser for Finelib category pages."""

    def find_business_cards(self, html: str) -> list[Tag]:
        """
        Return every business listing node.
        """
        soup = BeautifulSoup(html, "lxml")

        cards = soup.select("div.box-682.bg-none")

        return list(cards)

    

    def parse(self, html: str) -> list[RawDiscovery]:
        raise NotImplementedError

    def has_next_page(
        self,
        html: str,
    ) -> bool:

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
            return False

        for link in paging.find_all("a"):

            text = link.get_text(
                strip=True,
            )

            if text != "Next":
                continue

            return link.has_attr(
                "href",
            )

        return False

    def next_page_url(
        self,
        html: str,
    ) -> str | None:

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

            if isinstance(
                href,
                str,
            ):
                return href

            return None

        return None
