from __future__ import annotations

from acios_discovery.domain.cac import (
    CacEntityType,
    CacRegistrationStatus,
    CacSearchResult,
    CacVerificationResult,
    VerificationOutcome,
)
from acios_discovery.infrastructure.persistence.orm.cac_verification import (
    CacVerificationORM,
)


class CacVerificationMapper:
    """
    Converts between CacVerificationResult and its ORM row.
    """

    @staticmethod
    def to_orm(
        result: CacVerificationResult,
    ) -> CacVerificationORM:

        matched = result.matched_entity

        return CacVerificationORM(
            company_id=result.company_id,
            searched_name=result.searched_name,
            outcome=result.outcome.value,
            confidence=result.confidence,
            matched_approved_name=(
                matched.approved_name if matched else None
            ),
            matched_rc_number=(
                matched.rc_number if matched else None
            ),
            matched_company_id=(
                matched.company_id if matched else None
            ),
            matched_entity_type=(
                matched.entity_type.value if matched else None
            ),
            matched_registration_date=(
                matched.registration_date if matched else None
            ),
            matched_registration_status=(
                matched.status.value
                if matched and matched.status is not None
                else None
            ),
            matched_nature_of_business=(
                matched.nature_of_business if matched else None
            ),
            verified_at=result.verified_at,
        )

    @staticmethod
    def to_domain(
        orm: CacVerificationORM,
    ) -> CacVerificationResult:

        matched_entity: CacSearchResult | None = None

        if orm.outcome == VerificationOutcome.VERIFIED.value:

            #
            # These columns are nullable at the schema level
            # (since they're empty for AMBIGUOUS/NOT_FOUND rows),
            # but a VERIFIED row is always written with a full
            # matched-candidate snapshot by CacVerificationMapper
            # .to_orm() and CacVerificationService. The asserts
            # below make that invariant explicit and checked,
            # rather than silently assumed.
            #

            assert orm.matched_approved_name is not None
            assert orm.matched_company_id is not None
            assert orm.matched_entity_type is not None

            matched_entity = CacSearchResult(
                approved_name=orm.matched_approved_name,
                rc_number=orm.matched_rc_number,
                company_id=orm.matched_company_id,
                entity_type=CacEntityType(
                    orm.matched_entity_type,
                ),
                registration_date=orm.matched_registration_date,
                nature_of_business=orm.matched_nature_of_business or "",
                status=(
                    CacRegistrationStatus(
                        orm.matched_registration_status,
                    )
                    if orm.matched_registration_status is not None
                    else None
                ),
            )

        return CacVerificationResult(
            company_id=orm.company_id,
            searched_name=orm.searched_name,
            outcome=VerificationOutcome(orm.outcome),
            matched_entity=matched_entity,
            confidence=orm.confidence,
            verified_at=orm.verified_at,
        )
