from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from .user_id import UserId
from .user_role import UserRole


@dataclass(slots=True)
class User:
    """
    An account authorized to use the discovery dashboard/API.
    """

    id: UserId

    email: str

    hashed_password: str

    role: UserRole = UserRole.MEMBER

    active: bool = True

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
