from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from acios_discovery.infrastructure.persistence.metadata import Base


class CompanySetFieldProvenanceORM(Base):
    """
    Records which discovery contributed one specific value
    within a set-typed Company field (e.g. one phone number
    among several), and at what confidence.

    One row per (company_id, field_name, value).
    """

    __tablename__ = "company_set_field_provenance"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "field_name",
            "value",
            name="uq_company_set_provenance_field_value",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
    )

    field_name: Mapped[str] = mapped_column(
        String(64),
    )

    value: Mapped[str] = mapped_column(
        String(1024),
    )

    source: Mapped[str] = mapped_column(
        String(255),
    )

    detail_url: Mapped[str | None] = mapped_column(
        String(1024),
    )

    confidence: Mapped[float] = mapped_column(
        Float,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    company = relationship(
        "CompanyORM",
        back_populates="set_provenance_rows",
    )
