from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from acios_discovery.infrastructure.persistence.metadata import Base


class UserORM(Base):

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="member",
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
