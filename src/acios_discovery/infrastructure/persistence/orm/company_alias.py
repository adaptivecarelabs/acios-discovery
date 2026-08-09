from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from acios_discovery.infrastructure.persistence.metadata import Base


class CompanyAliasORM(Base):
    """
    Persisted company alias.

    Each alias belongs to exactly one canonical company.
    """

    __tablename__ = "company_aliases"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
        nullable=False,
    )

    value: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    normalized_value: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    company = relationship(
        "CompanyORM",
        back_populates="aliases",
    )
