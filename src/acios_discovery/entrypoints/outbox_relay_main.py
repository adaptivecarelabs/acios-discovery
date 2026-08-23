from __future__ import annotations

import asyncio
import signal

from acios_discovery.application.events.outbox_relay import OutboxRelay
from acios_discovery.infrastructure.events.logging_event_publisher import (
    LoggingEventPublisher,
)
from acios_discovery.infrastructure.persistence.database import (
    SessionFactory,
)
from acios_discovery.infrastructure.persistence.repositories.outbox_repository import (
    SqlAlchemyOutboxRepository,
)
from acios_discovery.shared.logging import logger

POLL_INTERVAL_SECONDS = 5


async def run() -> None:

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            stop_event.set,
        )

    logger.info(
        "Outbox relay started (poll interval: %ss)",
        POLL_INTERVAL_SECONDS,
    )

    while not stop_event.is_set():

        async with SessionFactory() as session:

            repository = SqlAlchemyOutboxRepository(
                session,
            )

            relay = OutboxRelay(
                repository=repository,
                publisher=LoggingEventPublisher(),
            )

            published = await relay.poll_once()

            await session.commit()

            if published:
                logger.info(
                    "Published %s event(s)",
                    published,
                )

        try:
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=POLL_INTERVAL_SECONDS,
            )
        except TimeoutError:
            pass

    logger.info(
        "Outbox relay stopped",
    )


def main() -> None:
    asyncio.run(
        run(),
    )


if __name__ == "__main__":
    main()
