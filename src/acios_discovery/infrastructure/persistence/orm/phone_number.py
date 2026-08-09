from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from acios_discovery.infrastructure.persistence.metadata import Base


class PhoneNumberORM(Base):

    __tablename__ = "company_phone_numbers"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
    )

    value: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    normalized_value: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )

    company = relationship(
        "CompanyORM",
        back_populates="phone_numbers",
    )
