from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.discovery.models import RawDiscovery


@dataclass(slots=True)
class Company:
    """
    Canonical Company Aggregate.

    This represents the master company registry.

    Multiple RawDiscoveries from one or more sources
    are merged into a single Company.
    """

    id: CompanyId

    canonical_name: str

    description: str | None = None

    #
    # Identity
    #

    aliases: set[str] = field(default_factory=set)

    phone_numbers: set[str] = field(default_factory=set)

    emails: set[str] = field(default_factory=set)

    websites: set[str] = field(default_factory=set)

    addresses: set[str] = field(default_factory=set)

    #
    # Classification
    #

    categories: set[str] = field(default_factory=set)

    cities: set[str] = field(default_factory=set)

    states: set[str] = field(default_factory=set)

    sources: set[str] = field(default_factory=set)

    #
    # Enrichment
    #

    social_links: dict[str, str] = field(default_factory=dict)

    product_types: set[str] = field(default_factory=set)

    payment_methods: set[str] = field(default_factory=set)

    year_founded: int | None = None

    employee_count: str | None = None

    business_locations: int | None = None

    #
    # Metadata
    #

    first_seen: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    last_seen: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    confidence: float = 100.0

    active: bool = True

    def touch(self) -> None:
        self.last_seen = datetime.now(UTC)

    def add_alias(self, value: str | None) -> None:
        if value:
            self.aliases.add(value.strip())

    def add_phone(self, value: str | None) -> None:
        if value:
            self.phone_numbers.add(value)

    def add_email(self, value: str | None) -> None:
        if value:
            self.emails.add(value)

    def add_website(self, value: str | None) -> None:
        if value:
            self.websites.add(value)

    def add_address(self, value: str | None) -> None:
        if value:
            self.addresses.add(value)

    def add_source(self, value: str | None) -> None:
        if value:
            self.sources.add(value)

    def merge_discovery(
        self,
        discovery: RawDiscovery,
    ) -> None:
        """
        Merge information from a new discovery
        into the canonical company aggregate.
        """

        self.add_alias(
            discovery.business_name,
        )

        for phone in discovery.phone_numbers:
            self.add_phone(phone)

        self.add_email(
            discovery.email,
        )

        self.add_website(
            discovery.website,
        )

        self.add_address(
            discovery.address,
        )

        if discovery.category:
            self.categories.add(
                discovery.category,
            )

        if discovery.city:
            self.cities.add(
                discovery.city,
            )

        if discovery.state:
            self.states.add(
                discovery.state,
            )

        self.add_source(
            discovery.source,
        )

        self.social_links.update(
            discovery.social_links,
        )

        self.product_types.update(
            discovery.product_types,
        )

        self.payment_methods.update(
            discovery.payment_methods,
        )

        if discovery.year_founded is not None:
            self.year_founded = (
                discovery.year_founded
            )

        if discovery.employee_count is not None:
            self.employee_count = (
                discovery.employee_count
            )

        if discovery.business_locations is not None:
            self.business_locations = (
                discovery.business_locations
            )

        self.touch()
