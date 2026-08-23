from __future__ import annotations

from acios_discovery.application.events.outbox_repository import (
    OutboxRepository,
)
from acios_discovery.domain.events.event_publisher import EventPublisher
from acios_discovery.shared.logging import logger


class OutboxRelay:
    """
    Drains the transactional outbox by publishing unpublished
    messages and recording the outcome of each attempt.

    One poll cycle processes up to `batch_size` messages. A
    failure publishing one message is recorded and does not
    prevent the remaining messages in the batch from being
    attempted.

    Messages that have failed `max_attempts` times are marked
    dead-lettered and excluded from all future poll cycles by
    OutboxRepository.get_unpublished(). They are not retried
    again automatically; recovering a dead-lettered message
    requires manual intervention (clearing dead_lettered_at).
    """

    def __init__(
        self,
        *,
        repository: OutboxRepository,
        publisher: EventPublisher,
        batch_size: int = 100,
        max_attempts: int = 5,
    ) -> None:
        self._repository = repository
        self._publisher = publisher
        self._batch_size = batch_size
        self._max_attempts = max_attempts

    async def poll_once(self) -> int:
        """
        Process one batch of unpublished messages.

        Returns the number of messages successfully published.
        """

        messages = await self._repository.get_unpublished(
            limit=self._batch_size,
        )

        published_count = 0

        for message in messages:

            if message.attempts >= self._max_attempts:

                logger.warning(
                    "Skipping exhausted event %s (%s): "
                    "%s attempts >= max %s. This message is "
                    "NOT dead-lettered and will be retried "
                    "again on a future poll cycle.",
                    message.event_type,
                    message.id,
                    message.attempts,
                    self._max_attempts,
                )

                await self._repository.mark_dead_lettered(
                    message.id,
                )

                continue

            try:
                await self._publisher.publish(
                    message,
                )

            except Exception as exc:

                logger.warning(
                    "Failed to publish event %s (%s): %s",
                    message.event_type,
                    message.id,
                    exc,
                )

                await self._repository.mark_failed(
                    message.id,
                    str(exc),
                )

                continue

            await self._repository.mark_published(
                message.id,
            )

            published_count += 1

        return published_count
