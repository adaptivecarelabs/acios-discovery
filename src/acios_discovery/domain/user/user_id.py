from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class UserId:
    """
    Immutable identifier for a User.
    """

    value: str

    PREFIX = "ACL-USR"

    @classmethod
    def from_sequence(
        cls,
        sequence: int,
    ) -> UserId:

        if sequence < 1:
            raise ValueError(
                "sequence must be positive",
            )

        return cls(
            f"{cls.PREFIX}-{sequence:08d}",
        )

    @classmethod
    def parse(
        cls,
        value: str,
    ) -> UserId:

        if not value.startswith(
            f"{cls.PREFIX}-",
        ):
            raise ValueError(
                "Invalid UserId",
            )

        return cls(
            value,
        )

    def __str__(
        self,
    ) -> str:

        return self.value
