from __future__ import annotations

from bs4 import Tag

from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.infrastructure.connectors.html import (
    extract_link,
    extract_phone_list,
    extract_text,
)


class FinelibMapper:
    """
    Maps one Finelib business card into a RawDiscovery.
    """

    def extract_business_name(
        self,
        card: Tag,
    ) -> str:
        """
        Extract business name.
        """

        return extract_text(
            card,
            "div.box-headings a",
        )

    def extract_detail_url(
        self,
        card: Tag,
    ) -> str:
        """
        Extract Finelib detail page URL.
        """

        return extract_link(
            card,
            "div.cmpny-lstng.url a",
        )

    def extract_address(
        self,
        card: Tag,
    ) -> str:
        """
        Extract business address.
        """

        return extract_text(
            card,
            "div.listing-info-img > div.cmpny-lstng-1",
        )

    def map(
        self,
        card: Tag,
    ) -> RawDiscovery:
        return RawDiscovery(
            source="finelib",
            business_name=self.extract_business_name(
                card
            ),
            detail_url=self.extract_detail_url(
                card
            ),
            address=self.extract_address(
                card
            ),
            phone_numbers=self.extract_phone_numbers(card),
        )


    def extract_phone_numbers(
        self,
        card: Tag,
    ) -> list[str]:
        """
        Extract all phone numbers from a listing.
        """

        raw = extract_text(
            card,
            "div.tel-no-div div.cmpny-lstng-1",
        )

        return extract_phone_list(raw)


    def extract_description(
        self,
        card: Tag,
    ) -> str:
        """
        Extract the company description from a
        Finelib business card.

        Returns an empty string if no description exists.
        """

        description = card.select_one(
            ".listing-desc p",
        )

        if description is None:
            return ""

        return description.get_text(
            " ",
            strip=True,
        )
