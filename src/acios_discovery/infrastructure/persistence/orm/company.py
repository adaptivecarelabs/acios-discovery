from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from acios_discovery.infrastructure.persistence.metadata import Base


class CompanyORM(Base):

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    canonical_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    canonical_name_normalized: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    description: Mapped[str | None]

    confidence: Mapped[float] = mapped_column(
        Float,
        default=100,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    year_founded: Mapped[int | None]

    employee_count: Mapped[str | None]

    business_locations: Mapped[int | None]

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    rc_number: Mapped[str | None] = mapped_column(
        String(64),
    )

    entity_type: Mapped[str | None] = mapped_column(
        String(32),
    )

    registration_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    registration_status: Mapped[str | None] = mapped_column(
        String(16),
    )

    nature_of_business: Mapped[str | None] = mapped_column(
        String(255),
    )

    cac_verifications = relationship(
        "CacVerificationORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    discoveries = relationship(
        "DiscoveryORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    emails = relationship(
        "EmailORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    websites = relationship(
        "WebsiteORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    addresses = relationship(
        "AddressORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    phone_numbers = relationship(
        "PhoneNumberORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    social_links = relationship(
        "SocialLinkORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    product_types = relationship(
        "ProductTypeORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    payment_methods = relationship(
        "PaymentMethodORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    categories = relationship(
        "CategoryORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    cities = relationship(
        "CityORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    states = relationship(
        "StateORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    aliases = relationship(
        "CompanyAliasORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    sources = relationship(
        "SourceORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    scalar_provenance_rows = relationship(
        "CompanyScalarFieldProvenanceORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    set_provenance_rows = relationship(
        "CompanySetFieldProvenanceORM",
        back_populates="company",
        cascade="all, delete-orphan",
    )
