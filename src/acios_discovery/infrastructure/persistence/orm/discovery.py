from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from acios_discovery.infrastructure.persistence.metadata import Base


class DiscoveryORM(Base):

    __tablename__ = "discoveries"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    #
    # Resolution
    #

    resolved_company_id: Mapped[str | None] = mapped_column(
        ForeignKey("companies.id"),
        nullable = True,
        index = True,
    )

    resolution_status: Mapped[str] = mapped_column(
        default="PENDING",
    )

    resolved_at: Mapped[datetime | None]

    source: Mapped[str]

    business_name: Mapped[str]

    address: Mapped[str | None]

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    detail_url: Mapped[str | None]

    #
    # Detail enrichment
    #

    phone_numbers: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    email: Mapped[str | None]

    website: Mapped[str | None]

    social_links: Mapped[dict[str, str]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    product_types: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    payment_methods: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    year_founded: Mapped[int | None]

    employee_count: Mapped[str | None]

    business_locations: Mapped[int | None]

    #
    # Discovery Context
    #

    country: Mapped[str]

    state: Mapped[str]

    city: Mapped[str]

    root: Mapped[str | None]

    industry: Mapped[str | None]

    sector: Mapped[str | None]

    category: Mapped[str]

    subcategory: Mapped[str | None]

    listing_url: Mapped[str]

    page_number: Mapped[int]

    #
    # Timestamp
    #

    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    company = relationship(
        "CompanyORM",
        back_populates="discoveries",
    )
