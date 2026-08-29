from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from acios_discovery.infrastructure.persistence.metadata import Base


class CacVerificationORM(Base):
    """
    Audit record of one attempt to verify a company against
    CAC's register — one row per attempt, not one row per
    company. A company may accumulate several rows over time
    (e.g. an initial NOT_FOUND followed by a later manual
    re-trigger that resolves to VERIFIED); the most recent
    VERIFIED row is what CompanyORM's own rc_number/entity_type/
    registration_date/registration_status/nature_of_business
    columns reflect.
    """

    __tablename__ = "cac_verifications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
    )

    searched_name: Mapped[str] = mapped_column(
        String(255),
    )

    outcome: Mapped[str] = mapped_column(
        String(16),
        index=True,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
    )

    #
    # Matched candidate snapshot — populated only when
    # outcome == VERIFIED. CAC search results are not
    # independently persisted anywhere else, so the match is
    # captured here at verification time for audit purposes.
    #

    matched_approved_name: Mapped[str | None] = mapped_column(
        String(255),
    )

    matched_rc_number: Mapped[str | None] = mapped_column(
        String(64),
    )

    matched_company_id: Mapped[int | None] = mapped_column(
        Integer,
    )

    matched_entity_type: Mapped[str | None] = mapped_column(
        String(32),
    )

    matched_registration_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    matched_registration_status: Mapped[str | None] = mapped_column(
        String(16),
    )

    matched_nature_of_business: Mapped[str | None] = mapped_column(
        String(255),
    )

    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    company = relationship(
        "CompanyORM",
        back_populates="cac_verifications",
    )
