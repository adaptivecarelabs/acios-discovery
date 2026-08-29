"""
Imports every ORM model so SQLAlchemy registers every table.

Importing ORM classes is intentionally side-effect free with respect
to business logic. It only registers their tables with Base.metadata.
"""

from acios_discovery.infrastructure.persistence.orm import (
    AddressORM,
    CategoryORM,
    CityORM,
    CompanyORM,
    CrawlJobORM,
    CrawlSessionORM,
    DiscoveryORM,
    EmailORM,
    OutboxEventORM,
    PaymentMethodORM,
    PhoneNumberORM,
    ProductTypeORM,
    SocialLinkORM,
    SourceORM,
    StateORM,
    UserORM,
    WebsiteORM,
)

__all__ = [
    "AddressORM",
    "CategoryORM",
    "CityORM",
    "CompanyORM",
    "CrawlJobORM",
    "CrawlSessionORM",
    "DiscoveryORM",
    "EmailORM",
    "OutboxEventORM",
    "PaymentMethodORM",
    "PhoneNumberORM",
    "ProductTypeORM",
    "SocialLinkORM",
    "SourceORM",
    "StateORM",
    "UserORM",
    "WebsiteORM",
]
