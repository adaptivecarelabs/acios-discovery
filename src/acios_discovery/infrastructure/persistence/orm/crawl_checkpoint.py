from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from acios_discovery.infrastructure.persistence.metadata import Base


class CrawlCheckpointORM(Base):
    """
    Durable checkpoint for crawl-session resume.

    There is one current checkpoint per crawl session.
    """

    __tablename__ = "crawl_checkpoints"

    session_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
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

    company_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
