from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from acios_discovery.infrastructure.persistence.metadata import Base


class CrawlJobORM(Base):
    """
    Durable representation of one crawl unit.

    Job state is authoritative for execution, retry, lease,
    heartbeat, and resume/recovery behaviour.
    """

    __tablename__ = "crawl_jobs"

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "source",
            "state",
            "city",
            "category_slug",
            name="uq_crawl_jobs_session_plan",
        ),
    )


    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey(
            "crawl_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    listing_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    category_slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    page: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        index=True,
    )

    retries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    max_retries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    last_completed_page: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_pages: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    lease_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    session = relationship(
        "CrawlSessionORM",
        back_populates="jobs",
    )
