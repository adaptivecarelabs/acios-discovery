from __future__ import annotations

from acios_discovery.domain.crawling.crawl_state import CrawlState


class InvalidStateTransition(Exception):
    """
    Raised when an invalid crawl state transition occurs.
    """


class CrawlStateMachine:
    """
    Controls crawl lifecycle transitions.
    """

    def __init__(self) -> None:

        self._state = CrawlState.CREATED

    @property
    def state(self) -> CrawlState:

        return self._state

    def initialize(self) -> None:

        self._transition(
            CrawlState.CREATED,
            CrawlState.INITIALIZING,
        )

    def start(self) -> None:

        if self._state not in (
            CrawlState.INITIALIZING,
            CrawlState.RESUMING,
        ):
            raise InvalidStateTransition(
                f"Cannot start from {self._state}"
            )

        self._state = CrawlState.RUNNING

    def pause(self) -> None:

        self._transition(
            CrawlState.RUNNING,
            CrawlState.PAUSED,
        )

    def resume(self) -> None:

        self._transition(
            CrawlState.PAUSED,
            CrawlState.RESUMING,
        )

    def complete(self) -> None:

        self._transition(
            CrawlState.RUNNING,
            CrawlState.COMPLETED,
        )

    def fail(self) -> None:

        if self._state in (
            CrawlState.COMPLETED,
            CrawlState.CANCELLED,
        ):
            raise InvalidStateTransition(
                f"Cannot fail from {self._state}"
            )

        self._state = CrawlState.FAILED

    def cancel(self) -> None:

        if self._state in (
            CrawlState.COMPLETED,
            CrawlState.FAILED,
        ):
            raise InvalidStateTransition(
                f"Cannot cancel from {self._state}"
            )

        self._state = CrawlState.CANCELLED

    def _transition(
        self,
        expected: CrawlState,
        new: CrawlState,
    ) -> None:

        if self._state != expected:
            raise InvalidStateTransition(
                f"Cannot transition "
                f"{self._state} -> {new}"
            )

        self._state = new
