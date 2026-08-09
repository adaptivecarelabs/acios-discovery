from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from acios_discovery.infrastructure.persistence.metadata import Base


class AddressORM(Base):

    __tablename__ = "company_addresses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
    )

    value: Mapped[str] = mapped_column(
        Text,
    )

    company = relationship(
        "CompanyORM",
        back_populates="addresses",
    )
