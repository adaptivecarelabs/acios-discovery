from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class EventSerializer:
    """
    Converts application/domain events into JSON-compatible
    outbox payloads.
    """

    @staticmethod
    def serialize(event: object) -> dict[str, Any]:
        """
        Convert a domain/application event into a JSON-safe
        dictionary suitable for PostgreSQL JSONB.
        """

        if not is_dataclass(event):
            raise TypeError(
                "Event must be a dataclass: "
                f"{type(event).__name__}"
            )

        payload = EventSerializer._convert(
            event,
        )

        if not isinstance(payload, dict):
            raise TypeError(
                "Serialized event payload must be a dictionary"
            )

        return payload

    @staticmethod
    def _convert(value: Any) -> Any:
        """
        Recursively convert supported Python objects into
        JSON-compatible values.
        """

        if value is None:
            return None

        if isinstance(
            value,
            (str, int, float, bool),
        ):
            return value

        if isinstance(value, Enum):
            return EventSerializer._convert(
                value.value,
            )

        if isinstance(
            value,
            (datetime, date),
        ):
            return value.isoformat()

        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, BaseModel):
            return EventSerializer._convert(
                value.model_dump(
                    mode="json",
                ),
            )

        if is_dataclass(value) and not isinstance(value, type):
            return {
                field.name: EventSerializer._convert(
                    getattr(value, field.name),
                )
                for field in fields(value)
            }

        if isinstance(value, dict):
            return {
                str(key): EventSerializer._convert(
                    item,
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                EventSerializer._convert(
                    item,
                )
                for item in value
            ]

        raise TypeError(
            "Unsupported event payload type: "
            f"{type(value).__name__}",
        )


def serialize_event(event: object) -> dict[str, Any]:
    """Serialize an application event into a JSON-safe payload."""
    return EventSerializer.serialize(event)
