from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.application.events.outbox import OutboxMessage


class EventPublisher(ABC):
    """
    Publishes a durable outbox message to its real destination
    (a message broker, webhook, log sink, etc).

    Implementations should raise on failure; the relay is
    responsible for retry/failure bookkeeping, not the publisher.
    """

    @abstractmethod
    async def publish(
        self,
        message: OutboxMessage,
    ) -> None:
        ...
