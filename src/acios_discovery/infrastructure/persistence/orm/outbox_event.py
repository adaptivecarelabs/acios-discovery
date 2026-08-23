from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from acios_discovery.infrastructure.persistence.metadata import Base


class OutboxEventORM(Base):
    """
    Durable representation of an application event.

    Events are written to the outbox inside the same database
    transaction as the business operation that produced them.
    """

    __tablename__ = "outbox_events"

    __table_args__ = (
        Index(
            "ix_outbox_events_unpublished",
            "published_at",
            "created_at",
        ),
        Index(
            "ix_outbox_events_event_type",
            "event_type",
        ),
        Index(
            "ix_outbox_events_aggregate",
            "aggregate_type",
            "aggregate_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    event_type: Mapped[str] = mapped_column(
        nullable=False,
    )

    aggregate_type: Mapped[str] = mapped_column(
        nullable=False,
    )

    aggregate_id: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    dead_lettered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
