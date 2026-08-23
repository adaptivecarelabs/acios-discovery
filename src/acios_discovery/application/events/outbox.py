from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, frozen=True)
class OutboxMessage:
    id: UUID
    event_type: str
    aggregate_type: str
    aggregate_id: str | None
    payload: dict
    occurred_at: datetime
    created_at: datetime
    attempts: int = 0
