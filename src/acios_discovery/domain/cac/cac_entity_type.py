from enum import StrEnum


class CacEntityType(StrEnum):
    """
    CAC's classification of a registered entity.

    Mirrors CAC's own `classificationName` values exactly, so no
    translation/mapping table is needed at the parsing boundary.

    classificationId (CAC's numeric counterpart, not modeled
    here) observed alongside each: BUSINESS_NAME=1, COMPANY=2,
    IT=3, LP=4, LLP=5.
    """

    BUSINESS_NAME = "BUSINESS_NAME"
    """A sole proprietorship / registered business name."""

    COMPANY = "COMPANY"
    """A limited company (Ltd, Plc, etc.)."""

    IT = "IT"
    """Incorporated Trustee — associations, foundations, NGOs."""

    LP = "LP"
    """Limited Partnership."""

    LLP = "LLP"
    """Limited Liability Partnership."""
