from enum import StrEnum


class VerificationOutcome(StrEnum):
    """
    Result of attempting to verify a discovered company against
    CAC.
    """

    VERIFIED = "verified"
    """A single CAC candidate cleared the confidence threshold."""

    NOT_FOUND = "not_found"
    """CAC's search returned no candidates at all."""

    AMBIGUOUS = "ambiguous"
    """
    CAC returned candidates, but none cleared the confidence
    threshold required to auto-accept a match.
    """
