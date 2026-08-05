from __future__ import annotations

from acios_discovery.application.normalization.canonical_business_name import (
    CanonicalBusinessNameNormalizer,
)
from acios_discovery.application.resolution.field_similarity import (
    address_match,
    phone_match,
    same_domain,
    similarity,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.discovery.models import RawDiscovery


class EntityResolutionEngine:
    """
    Calculates the confidence that an incoming
    RawDiscovery belongs to an existing Company.
    """

    NAME_WEIGHT = 60.0
    PHONE_WEIGHT = 20.0
    WEBSITE_WEIGHT = 10.0
    EMAIL_WEIGHT = 5.0
    ADDRESS_WEIGHT = 5.0

    def __init__(self) -> None:
        self._normalizer = CanonicalBusinessNameNormalizer()

    def confidence(
        self,
        discovery: RawDiscovery,
        company: Company,
    ) -> float:

        #
        # Same object shortcut
        #

        if getattr(company, "source_discovery", None) is discovery:
            return 100.0

        score = 0.0

        #
        # ---------- NAME ----------
        #

        discovery_name = self._normalizer.normalize(
            discovery.business_name,
        )

        names = {
            company.canonical_name,
            *company.aliases,
        }

        best_name = 0.0

        for name in names:

            best_name = max(
                best_name,
                similarity(
                    discovery_name,
                    self._normalizer.normalize(name),
                ),
            )

        score += best_name * self.NAME_WEIGHT

        #
        # ---------- PHONE ----------
        #

        if discovery.phone_numbers:

            for incoming in discovery.phone_numbers:

                if any(
                    phone_match(
                        incoming,
                        existing,
                    )
                    for existing in company.phone_numbers
                ):
                    score += self.PHONE_WEIGHT
                    break

        #
        # ---------- WEBSITE ----------
        #

        if discovery.website:

            if any(
                same_domain(
                    discovery.website,
                    existing,
                )
                for existing in company.websites
            ):
                score += self.WEBSITE_WEIGHT

        #
        # ---------- EMAIL ----------
        #

        if discovery.email:

            if discovery.email in company.emails:
                score += self.EMAIL_WEIGHT

        #
        # ---------- ADDRESS ----------
        #

        if discovery.address:

            if any(
                address_match(
                    discovery.address,
                    existing,
                )
                for existing in company.addresses
            ):
                score += self.ADDRESS_WEIGHT

        return round(score, 2)

    def is_duplicate(
        self,
        discovery: RawDiscovery,
        company: Company,
        threshold: float = 80.0,
    ) -> bool:

        return (
            self.confidence(
                discovery,
                company,
            )
            >= threshold
        )
