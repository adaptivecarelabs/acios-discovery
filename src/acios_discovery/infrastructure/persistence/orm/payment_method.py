from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from acios_discovery.infrastructure.persistence.metadata import Base


class PaymentMethodORM(Base):

    __tablename__ = "company_payment_methods"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
    )

    value: Mapped[str]

    company = relationship(
        "CompanyORM",
        back_populates="payment_methods",
    )
