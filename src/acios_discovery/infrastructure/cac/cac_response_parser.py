from __future__ import annotations

from datetime import datetime

from acios_discovery.domain.cac import (
    CacEntityType,
    CacRegistrationStatus,
    CacSearchResult,
)
from acios_discovery.shared.logging import logger


class CacResponseParser:
    """
    Parses CAC's public search API response into CacSearchResult
    objects.

    CAC's real responses are meaningfully messier than the happy
    path: rc_number and companyRegistrationDate are frequently
    null (observed across IT/LP/LLP entities and some COMPANY/
    BUSINESS_NAME entries too), status can be an empty string
    rather than a valid enum value, and occasionally an entire
    row is null/empty across every field (approvedName included)
    — these carry no usable signal and are dropped rather than
    producing a CacSearchResult with no name to match against.
    """

    def parse(
        self,
        payload: dict,
    ) -> list[CacSearchResult]:

        raw_results = payload.get("data", [])

        results: list[CacSearchResult] = []

        for raw in raw_results:

            parsed = self._parse_one(raw)

            if parsed is not None:
                results.append(parsed)

        return results

    def _parse_one(
        self,
        raw: dict,
    ) -> CacSearchResult | None:

        approved_name = raw.get("approvedName")

        if not approved_name:
            # No name at all — nothing to match against, and
            # CAC does return fully-null placeholder rows.
            return None

        entity_type = self._parse_entity_type(
            raw.get("classificationName"),
        )

        if entity_type is None:
            logger.warning(
                "CAC search result for %r has an unrecognized "
                "classificationName %r — skipping.",
                approved_name,
                raw.get("classificationName"),
            )
            return None

        company_id = raw.get("companyId")

        if company_id is None:
            logger.warning(
                "CAC search result for %r has no companyId — "
                "skipping.",
                approved_name,
            )
            return None

        return CacSearchResult(
            approved_name=approved_name,
            rc_number=raw.get("rcNumber") or None,
            company_id=company_id,
            entity_type=entity_type,
            registration_date=self._parse_datetime(
                raw.get("companyRegistrationDate"),
            ),
            nature_of_business=(
                raw.get("natureOfBusiness") or ""
            ).strip(),
            status=self._parse_status(
                raw.get("status"),
            ),
        )

    def _parse_entity_type(
        self,
        value: str | None,
    ) -> CacEntityType | None:

        if not value:
            return None

        try:
            return CacEntityType(value)

        except ValueError:
            return None

    def _parse_status(
        self,
        value: str | None,
    ) -> CacRegistrationStatus | None:

        if not value:
            return None

        try:
            return CacRegistrationStatus(value)

        except ValueError:
            logger.warning(
                "CAC search result has an unrecognized status "
                "%r — treating as unknown.",
                value,
            )
            return None

    def _parse_datetime(
        self,
        value: str | None,
    ) -> datetime | None:

        if not value:
            return None

        try:
            # CAC's dates use "Z" suffix (Zulu/UTC) and variable
            # fractional-second precision — fromisoformat handles
            # the latter but not "Z" directly pre-3.11-normalized
            # forms in all cases, so normalize explicitly.
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)

        except ValueError:
            logger.warning(
                "CAC search result has an unparseable "
                "companyRegistrationDate %r — treating as "
                "unknown.",
                value,
            )
            return None
