from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class CompanyId:
    """
    Immutable identifier for a Company.
    """

    value: str

    PREFIX = "COMP"

    @classmethod
    def from_sequence(
        cls,
        sequence: int,
    ) -> CompanyId:

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
    ) -> CompanyId:

        if not value.startswith(
            f"{cls.PREFIX}-",
        ):
            raise ValueError(
                "Invalid CompanyId",
            )

        return cls(
            value,
        )

    def __str__(
        self,
    ) -> str:

        return self.value
