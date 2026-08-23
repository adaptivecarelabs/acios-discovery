from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FieldChange:
    """
    Describes what happened to a single field
    during a merge.
    """

    field_name: str

    old_value: Any

    new_value: Any

    accepted: bool

    reason: str


@dataclass(slots=True)
class MergeSummary:
    """
    Full record of what a merge did to a Company.
    """

    changes: list[FieldChange] = field(
        default_factory=list,
    )

    def record(
        self,
        field_name: str,
        old_value: Any,
        new_value: Any,
        accepted: bool,
        reason: str,
    ) -> None:

        self.changes.append(
            FieldChange(
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                accepted=accepted,
                reason=reason,
            )
        )

    @property
    def changed_fields(self) -> list[str]:
        return [
            change.field_name
            for change in self.changes
            if change.accepted
        ]
