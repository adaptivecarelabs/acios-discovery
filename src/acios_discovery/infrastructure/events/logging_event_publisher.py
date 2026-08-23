from __future__ import annotations

from acios_discovery.application.events.outbox import OutboxMessage
from acios_discovery.domain.events.event_publisher import EventPublisher
from acios_discovery.shared.logging import logger


class LoggingEventPublisher(EventPublisher):
    """
    Default EventPublisher.

    Logs every event instead of delivering it anywhere. This keeps
    the outbox relay fully wired and testable before a real message
    broker, webhook target, or downstream consumer exists.
    """

    async def publish(
        self,
        message: OutboxMessage,
    ) -> None:

        logger.info(
            "Publishing event %s (%s) for aggregate %s:%s",
            message.event_type,
            message.id,
            message.aggregate_type,
            message.aggregate_id,
        )
