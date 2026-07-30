import re


class BusinessNameNormalizer:
    """
    Produces a CAC-friendly search keyword
    from a raw business name.
    """

    _PATTERNS = (
        r"\bLIMITED\b",
        r"\bLTD\.?\b",
        r"\bPLC\b",
        r"\bNIG\.?\b",
        r"\bAND SONS\b",
        r"&\s*SONS\b",
    )

    def normalize(
        self,
        value: str,
    ) -> str:
        cleaned = value.strip()

        for pattern in self._PATTERNS:
            cleaned = re.sub(
                pattern,
                "",
                cleaned,
                flags=re.IGNORECASE,
            )

        # Remove leftover punctuation
        cleaned = re.sub(
            r"[.,]+",
            " ",
            cleaned,
        )

        # Collapse whitespace
        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        )

        return cleaned.strip()
