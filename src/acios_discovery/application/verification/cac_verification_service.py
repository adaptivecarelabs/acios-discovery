from __future__ import annotations

from rapidfuzz import fuzz

from acios_discovery.domain.cac import (
    CacSearchResult,
    CacVerificationResult,
    VerificationOutcome,
)
from acios_discovery.domain.company.company import Company
from acios_discovery.domain.shared.matching import normalize_text
from acios_discovery.infrastructure.cac.cac_search_client import (
    CacSearchClient,
)

DEFAULT_CONFIDENCE_THRESHOLD = 90.0

#
# Legal-entity suffix normalization, scoped to CAC matching only.
#
# CAC's register always spells these out in full (e.g.
# "LIMITED"), while discovered business names from directories
# like Finelib commonly use the abbreviated form ("LTD"). Without
# this, WRatio/token_sort_ratio treat "LTD" and "LIMITED" as
# different tokens and a large fraction of genuinely correct
# matches score just below any reasonable threshold.
#
# Only the trailing token is expanded — a mid-string "LTD" (e.g.
# a decoy candidate like "X LTD SUBSIDIARY") is a different,
# unrelated name and should not be silently rewritten.
#
_LEGAL_SUFFIX_EXPANSIONS = {
    "LTD": "LIMITED",
    "PLC": "PUBLIC LIMITED COMPANY",
    "INC": "INCORPORATED",
    "IT": "INCORPORATED TRUSTEE",
    "LP": "LIMITED PARTNERSHIP",
    "LLP": "LIMITED LIABILITY PARTNERSHIP",
}


def _expand_legal_suffix(value: str) -> str:

    words = value.split()

    if words and words[-1] in _LEGAL_SUFFIX_EXPANSIONS:
        words[-1] = _LEGAL_SUFFIX_EXPANSIONS[words[-1]]

    return " ".join(words)


def _prepare_for_matching(value: str) -> str:
    return _expand_legal_suffix(normalize_text(value))


class CacVerificationService:
    """
    Verifies a discovered Company against CAC's public register
    by searching on canonical_name and scoring each candidate's
    approved_name via fuzzy string similarity.

    Uses token_sort_ratio rather than WRatio: WRatio's internal
    partial-ratio logic rewards one string being a near-exact
    substring of another, which can rank an unrelated candidate
    whose name happens to start with the same words above the
    true match. token_sort_ratio does not have this bias and was
    verified empirically against representative CAC-style name
    variations before being chosen.

    Registration status (ACTIVE/INACTIVE) is NOT a scoring
    factor and never disqualifies a candidate — it is carried
    through purely as descriptive output on the matched entity.
    A candidate is judged solely on how closely its approved_name
    matches the searched company name.
    """

    def __init__(
        self,
        *,
        search_client: CacSearchClient,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> None:
        self._search_client = search_client
        self._threshold = confidence_threshold

    async def verify(
        self,
        company: Company,
    ) -> CacVerificationResult:

        searched_name = company.canonical_name

        candidates = await self._search_client.search(
            searched_name,
        )

        if not candidates:
            return CacVerificationResult(
                company_id=company.id.value,
                searched_name=searched_name,
                outcome=VerificationOutcome.NOT_FOUND,
                matched_entity=None,
                confidence=0.0,
            )

        best_candidate, best_score = self._best_match(
            searched_name,
            candidates,
        )

        if best_score >= self._threshold:
            return CacVerificationResult(
                company_id=company.id.value,
                searched_name=searched_name,
                outcome=VerificationOutcome.VERIFIED,
                matched_entity=best_candidate,
                confidence=best_score,
            )

        # Candidates exist, but nothing cleared the threshold —
        # ambiguous, not a hard failure. No matched_entity is
        # recorded since nothing was confidently selected.
        return CacVerificationResult(
            company_id=company.id.value,
            searched_name=searched_name,
            outcome=VerificationOutcome.AMBIGUOUS,
            matched_entity=None,
            confidence=best_score,
        )

    def _best_match(
        self,
        searched_name: str,
        candidates: list[CacSearchResult],
    ) -> tuple[CacSearchResult, float]:

        prepared_search = _prepare_for_matching(searched_name)

        scored = [
            (
                candidate,
                fuzz.token_sort_ratio(
                    prepared_search,
                    _prepare_for_matching(candidate.approved_name),
                ),
            )
            for candidate in candidates
        ]

        return max(scored, key=lambda pair: pair[1])
