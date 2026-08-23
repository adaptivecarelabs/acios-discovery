from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from acios_discovery.domain.company.company_id import CompanyId
from acios_discovery.domain.company.field_provenance import FieldProvenance
from acios_discovery.domain.company.merge_summary import MergeSummary
from acios_discovery.domain.discovery.models import RawDiscovery
from acios_discovery.domain.shared.matching import (
    address_match,
    normalize_text,
    phone_match,
    same_domain,
)


@dataclass(slots=True)
class Company:
    """
    Canonical Company Aggregate.

    This represents the master company registry.

    Multiple RawDiscoveries from one or more sources
    are merged into a single Company.
    """

    id: CompanyId

    canonical_name: str

    description: str | None = None

    #
    # Identity
    #

    aliases: set[str] = field(default_factory=set)

    phone_numbers: set[str] = field(default_factory=set)

    emails: set[str] = field(default_factory=set)

    websites: set[str] = field(default_factory=set)

    addresses: set[str] = field(default_factory=set)

    #
    # Classification
    #

    categories: set[str] = field(default_factory=set)

    cities: set[str] = field(default_factory=set)

    states: set[str] = field(default_factory=set)

    sources: set[str] = field(default_factory=set)

    #
    # Enrichment
    #

    social_links: dict[str, str] = field(default_factory=dict)

    product_types: set[str] = field(default_factory=set)

    payment_methods: set[str] = field(default_factory=set)

    year_founded: int | None = None

    employee_count: str | None = None

    business_locations: int | None = None

    #
    # Provenance
    #
    # set_provenance:    {field_name: {value: FieldProvenance}}
    # scalar_provenance: {field_name: FieldProvenance}
    #

    set_provenance: dict[str, dict[str, FieldProvenance]] = field(
        default_factory=dict,
    )

    scalar_provenance: dict[str, FieldProvenance] = field(
        default_factory=dict,
    )

    #
    # Metadata
    #

    first_seen: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    last_seen: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    confidence: float = 100.0

    active: bool = True

    def touch(self) -> None:
        self.last_seen = datetime.now(UTC)

    def add_alias(self, value: str | None) -> None:
        if value:
            self.aliases.add(value.strip())

    def add_phone(self, value: str | None) -> None:
        if value:
            self.phone_numbers.add(value)

    def add_email(self, value: str | None) -> None:
        if value:
            self.emails.add(value)

    def add_website(self, value: str | None) -> None:
        if value:
            self.websites.add(value)

    def add_address(self, value: str | None) -> None:
        if value:
            self.addresses.add(value)

    def add_source(self, value: str | None) -> None:
        if value:
            self.sources.add(value)

    #
    # ---------- Merge internals ----------
    #

    def _merge_set_field(
        self,
        field_name: str,
        incoming_values: Iterable[str],
        match: Callable[[str, str], bool],
        provenance: FieldProvenance,
        summary: MergeSummary,
    ) -> None:

        current: set[str] = getattr(self, field_name)

        field_provenance = self.set_provenance.setdefault(
            field_name,
            {},
        )

        for value in incoming_values:

            if not value:
                continue

            already_present = any(
                match(value, existing)
                for existing in current
            )

            if already_present:
                continue

            current.add(value)

            field_provenance[value] = provenance

            summary.record(
                field_name=field_name,
                old_value=None,
                new_value=value,
                accepted=True,
                reason="new_value",
            )

    def _merge_scalar_field(
        self,
        field_name: str,
        incoming_value: Any,
        confidence: float,
        provenance: FieldProvenance,
        summary: MergeSummary,
    ) -> None:

        if incoming_value is None:
            return

        current_value = getattr(self, field_name)

        if current_value is None:

            setattr(self, field_name, incoming_value)

            self.scalar_provenance[field_name] = provenance

            summary.record(
                field_name=field_name,
                old_value=None,
                new_value=incoming_value,
                accepted=True,
                reason="first_value",
            )

            return

        if incoming_value == current_value:
            return

        existing_provenance = self.scalar_provenance.get(
            field_name,
        )

        existing_confidence = (
            existing_provenance.confidence
            if existing_provenance is not None
            else 100.0
        )

        if confidence > existing_confidence:

            setattr(self, field_name, incoming_value)

            self.scalar_provenance[field_name] = provenance

            summary.record(
                field_name=field_name,
                old_value=current_value,
                new_value=incoming_value,
                accepted=True,
                reason="higher_confidence",
            )

        else:

            reason = (
                "tie_kept_existing"
                if confidence == existing_confidence
                else "lower_confidence"
            )

            summary.record(
                field_name=field_name,
                old_value=current_value,
                new_value=incoming_value,
                accepted=False,
                reason=reason,
            )

    def merge_discovery(
        self,
        discovery: RawDiscovery,
        *,
        confidence: float,
    ) -> MergeSummary:
        """
        Merge information from a new discovery into the
        canonical company aggregate.

        Set-typed fields are deduplicated against existing
        values using field-level matching, then added with
        provenance if genuinely new.

        Scalar fields are resolved by confidence: the incoming
        value only replaces the existing one if its confidence
        is strictly higher. Ties keep the existing value.
        """

        summary = MergeSummary()

        now = datetime.now(UTC)

        provenance = FieldProvenance(
            source=discovery.source,
            detail_url=discovery.detail_url,
            confidence=confidence,
            observed_at=now,
        )

        #
        # ---------- SET FIELDS ----------
        #

        self._merge_set_field(
            "aliases",
            [discovery.business_name],
            match=lambda a, b: normalize_text(a) == normalize_text(b),
            provenance=provenance,
            summary=summary,
        )

        self._merge_set_field(
            "phone_numbers",
            discovery.phone_numbers,
            match=phone_match,
            provenance=provenance,
            summary=summary,
        )

        if discovery.email:
            self._merge_set_field(
                "emails",
                [discovery.email],
                match=lambda a, b: a.strip().lower() == b.strip().lower(),
                provenance=provenance,
                summary=summary,
            )

        if discovery.website:
            self._merge_set_field(
                "websites",
                [discovery.website],
                match=same_domain,
                provenance=provenance,
                summary=summary,
            )

        if discovery.address:
            self._merge_set_field(
                "addresses",
                [discovery.address],
                match=address_match,
                provenance=provenance,
                summary=summary,
            )

        if discovery.category:
            self._merge_set_field(
                "categories",
                [discovery.category],
                match=lambda a, b: normalize_text(a) == normalize_text(b),
                provenance=provenance,
                summary=summary,
            )

        if discovery.city:
            self._merge_set_field(
                "cities",
                [discovery.city],
                match=lambda a, b: normalize_text(a) == normalize_text(b),
                provenance=provenance,
                summary=summary,
            )

        if discovery.state:
            self._merge_set_field(
                "states",
                [discovery.state],
                match=lambda a, b: normalize_text(a) == normalize_text(b),
                provenance=provenance,
                summary=summary,
            )

        self._merge_set_field(
            "product_types",
            discovery.product_types,
            match=lambda a, b: normalize_text(a) == normalize_text(b),
            provenance=provenance,
            summary=summary,
        )

        self._merge_set_field(
            "payment_methods",
            discovery.payment_methods,
            match=lambda a, b: normalize_text(a) == normalize_text(b),
            provenance=provenance,
            summary=summary,
        )

        self.add_source(discovery.source)

        self.social_links.update(discovery.social_links)

        #
        # ---------- SCALAR FIELDS ----------
        #

        self._merge_scalar_field(
            "description",
            discovery.description,
            confidence,
            provenance,
            summary,
        )

        self._merge_scalar_field(
            "year_founded",
            discovery.year_founded,
            confidence,
            provenance,
            summary,
        )

        self._merge_scalar_field(
            "employee_count",
            discovery.employee_count,
            confidence,
            provenance,
            summary,
        )

        self._merge_scalar_field(
            "business_locations",
            discovery.business_locations,
            confidence,
            provenance,
            summary,
        )

        self.touch()

        return summary
