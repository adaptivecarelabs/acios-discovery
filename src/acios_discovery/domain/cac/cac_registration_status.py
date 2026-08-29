from enum import StrEnum


class CacRegistrationStatus(StrEnum):
    """
    CAC's registration status for an entity.

    Mirrors CAC's own `status` values exactly.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
