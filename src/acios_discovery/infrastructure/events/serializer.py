from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


def serialize_event(event: Any) -> dict[str, Any]:
    """
    Convert a domain event into JSON-compatible data.
    """

    data = asdict(event)

    return _make_json_safe(data)


def _make_json_safe(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {
            str(key): _make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            _make_json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _make_json_safe(item)
            for item in value
        ]

    if hasattr(value, "model_dump"):
        return _make_json_safe(
            value.model_dump(),
        )

    return value
