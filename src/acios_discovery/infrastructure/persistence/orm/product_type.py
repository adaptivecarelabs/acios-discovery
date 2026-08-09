from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from acios_discovery.infrastructure.persistence.metadata import Base


class ProductTypeORM(Base):

    __tablename__ = "company_product_types"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
    )

    value: Mapped[str]

    company = relationship(
        "CompanyORM",
        back_populates="product_types",
    )
