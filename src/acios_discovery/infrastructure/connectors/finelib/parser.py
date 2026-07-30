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
