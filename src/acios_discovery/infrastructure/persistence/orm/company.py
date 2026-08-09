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
