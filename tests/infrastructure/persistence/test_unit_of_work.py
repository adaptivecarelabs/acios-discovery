from __future__ import annotations

from unittest.mock import AsyncMock

from acios_discovery.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


def test_unit_of_work_exposes_repositories(
    db_session,
) -> None:
    uow = SqlAlchemyUnitOfWork(
        db_session,
    )

    assert uow.discovery_repository is not None
    assert uow.outbox_repository is not None
    assert uow.company_repository is not None


async def test_unit_of_work_commit(
    db_session,
) -> None:
    db_session.commit = AsyncMock()

    uow = SqlAlchemyUnitOfWork(
        db_session,
    )

    await uow.commit()

    db_session.commit.assert_awaited_once()


async def test_unit_of_work_rollback(
    db_session,
) -> None:
    db_session.rollback = AsyncMock()

    uow = SqlAlchemyUnitOfWork(
        db_session,
    )

    await uow.rollback()

    db_session.rollback.assert_awaited_once()
