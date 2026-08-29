from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.cac import CacVerificationResult


class CacVerificationRepository(ABC):
    """
    Persists CAC verification attempts.

    This is an append-only audit log — one row per attempt, not
    one row per company. add() always inserts a new row rather
    than updating an existing one.
    """

    @abstractmethod
    async def add(
        self,
        result: CacVerificationResult,
    ) -> None:
        """
        Record a new verification attempt.
        """

    @abstractmethod
    async def get_latest_for_company(
        self,
        company_id: str,
    ) -> CacVerificationResult | None:
        """
        Return the most recent verification attempt for a
        company, or None if it has never been attempted.
        """

    @abstractmethod
    async def get_terminal_company_ids(
        self,
    ) -> set[str]:
        """
        Company ids with a terminal CAC verification outcome
        (VERIFIED or NOT_FOUND) on record.

        Used by the bulk verification job to exclude companies
        that have already reached a terminal state — a NOT_FOUND
        result requires an explicit manual re-trigger via the
        single-lookup endpoint, and a VERIFIED result needs no
        further attempts. Companies with only an AMBIGUOUS
        result, or with no attempt at all, are NOT included here
        and remain eligible for automatic retry on future batch
        runs.
        """
