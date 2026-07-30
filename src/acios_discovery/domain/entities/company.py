from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Company:
    """
    Canonical company within the discovery pipeline.
    """

    business_name: str
    rc_number: str
    status: str
    phone_number: str | None = None
    address: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.business_name.strip():
            raise ValueError("business_name cannot be empty")

        if not self.rc_number.strip():
            raise ValueError("rc_number cannot be empty")

        if not self.status.strip():
            raise ValueError("status cannot be empty")
