from __future__ import annotations

from enum import Enum


class EntityMatch(Enum):
    """
    Resolution outcome between
    two discovery records.
    """

    SAME = "same"

    STRONG_MATCH = "strong_match"

    POSSIBLE_MATCH = "possible_match"

    DIFFERENT = "different"
