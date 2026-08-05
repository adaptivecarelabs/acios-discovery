from __future__ import annotations

import re
import unicodedata


class CanonicalBusinessNameNormalizer:
    """
    Produces a canonical business name for
    entity resolution.

    Unlike BusinessNameNormalizer,
    this class does NOT prepare names
    for CAC searching.

    Instead it produces a stable
    canonical representation suitable
    for duplicate detection.
    """

    _CORPORATE_SUFFIXES = (
        r"\bLIMITED\b",
        r"\bLTD\.?\b",
        r"\bPLC\b",
        r"\bLLC\b",
        r"\bINC\b",
        r"\bINCORPORATED\b",
        r"\bCORPORATION\b",
        r"\bCORP\b",
        r"\bCO\.?\b",
        r"\bCOMPANY\b",
    )

    def normalize(
        self,
        value: str,
    ) -> str:

        if not value:
            return ""

        cleaned = unicodedata.normalize(
            "NFKD",
            value,
        )

        cleaned = cleaned.upper()

        for suffix in self._CORPORATE_SUFFIXES:
            cleaned = re.sub(
                suffix,
                "",
                cleaned,
            )

        cleaned = cleaned.replace(
            "&",
            " AND ",
        )

        cleaned = re.sub(
            r"[^A-Z0-9 ]",
            " ",
            cleaned,
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        )

        return cleaned.strip()
