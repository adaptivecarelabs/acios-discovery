from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from acios_discovery.infrastructure.persistence.metadata import Base


class CompanyScalarFieldProvenanceORM(Base):
    """
    Records which discovery established the currently-recorded
    value of one scalar Company field, and at what confidence.

    One row per (company_id, field_name).
    """

    __tablename__ = "company_scalar_field_provenance"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "field_name",
            name="uq_company_scalar_provenance_field",
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
        back_populates="scalar_provenance_rows",
    )
