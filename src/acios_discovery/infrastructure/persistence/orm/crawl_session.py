from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from acios_discovery.infrastructure.persistence.metadata import Base


class CrawlSessionORM(Base):
    """
    Durable record of one complete crawl execution.

    The database is the authoritative source of crawl execution
    progress and recovery state.
    """

    __tablename__ = "crawl_sessions"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    jobs_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_completed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_failed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    retries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    pages_crawled: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    companies_discovered: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    jobs = relationship(
        "CrawlJobORM",
        back_populates="session",
        cascade="all, delete-orphan",
    )

