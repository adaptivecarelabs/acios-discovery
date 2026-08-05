from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from acios_discovery.domain.company.company_id import (
    CompanyId,
)


@dataclass(slots=True)
class Company:
    """
    Master representation of a business.

    Multiple discoveries from different
    sources resolve into one Company.
    """

    id: CompanyId

    canonical_name: str

    aliases: set[str] = field(default_factory=set)

    phone_numbers: set[str] = field(default_factory=set)

    emails: set[str] = field(default_factory=set)

    websites: set[str] = field(default_factory=set)

    addresses: set[str] = field(default_factory=set)

    categories: set[str] = field(default_factory=set)

    cities: set[str] = field(default_factory=set)

    states: set[str] = field(default_factory=set)

    sources: set[str] = field(default_factory=set)

    first_seen: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    last_seen: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    confidence: float = 100.0

    active: bool = True

    def touch(self) -> None:
        """
        Updates the last_seen timestamp.
        """

        self.last_seen = datetime.now(
            UTC,
        )

    def add_alias(
        self,
        value: str,
    ) -> None:

        if value.strip():

            self.aliases.add(
                value.strip(),
            )

    def add_phone(
        self,
        value: str | None,
    ) -> None:

        if value:

            self.phone_numbers.add(
                value,
            )

    def add_email(
        self,
        value: str | None,
    ) -> None:

        if value:

            self.emails.add(
                value,
            )

    def add_website(
        self,
        value: str | None,
    ) -> None:

        if value:

            self.websites.add(
                value,
            )

    def add_address(
        self,
        value: str | None,
    ) -> None:

        if value:

            self.addresses.add(
                value,
            )

    def add_source(
        self,
        value: str,
    ) -> None:

        if value:

            self.sources.add(
                value,
            )
