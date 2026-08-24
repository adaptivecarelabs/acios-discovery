from __future__ import annotations

import time

from rich.progress import Progress, TaskID

from acios_discovery.domain.events.job_completed_event import (
    JobCompletedEvent,
)
from acios_discovery.domain.events.job_failed_event import (
    JobFailedEvent,
)


class ProgressBarSubscriber:
    """
    Advances a rich progress bar by one step for every job that
    reaches a terminal state (completed or failed), and tracks
    when the last such event happened so a heartbeat task can
    detect a stalled crawl.

    Intended for CLI presentation only — application/domain code
    has no dependency on this class.
    """

    def __init__(
        self,
        *,
        progress: Progress,
        task_id: TaskID,
    ) -> None:
        self._progress = progress
        self._task_id = task_id
        self.last_event_at = time.monotonic()

    async def __call__(
        self,
        event,
    ) -> None:

        if isinstance(
            event,
            (JobCompletedEvent, JobFailedEvent),
        ):
            self.last_event_at = time.monotonic()
            self._progress.advance(self._task_id)
