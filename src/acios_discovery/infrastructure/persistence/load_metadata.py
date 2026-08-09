"""
Imports every ORM model so SQLAlchemy registers every table.

Nothing in this file executes business logic.

Simply importing each ORM class ensures
Base.metadata.create_all() knows about every table.
"""

from acios_discovery.infrastructure.persistence.orm import (
    AddressORM,
    CategoryORM,
    CityORM,
    CompanyORM,
    DiscoveryORM,
    EmailORM,
    PaymentMethodORM,
    PhoneNumberORM,
    ProductTypeORM,
    SocialLinkORM,
    SourceORM,
    StateORM,
    WebsiteORM,
)

__all__ = [
    "AddressORM",
    "CategoryORM",
    "CityORM",
    "CompanyORM",
    "DiscoveryORM",
    "EmailORM",
    "PaymentMethodORM",
    "PhoneNumberORM",
    "ProductTypeORM",
    "SocialLinkORM",
    "SourceORM",
    "StateORM",
    "WebsiteORM",
]
