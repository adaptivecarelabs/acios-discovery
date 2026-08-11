import pytest

from acios_discovery.application.company.sequential_company_id_allocator import (
    SequentialCompanyIdAllocator,
)


@pytest.mark.anyio
async def test_allocator_returns_sequential_company_ids() -> None:
    allocator = SequentialCompanyIdAllocator()

    first = await allocator.allocate()
    second = await allocator.allocate()
    third = await allocator.allocate()

    assert str(first) == "ACL-COM-00000001"
    assert str(second) == "ACL-COM-00000002"
    assert str(third) == "ACL-COM-00000003"


@pytest.mark.anyio
async def test_allocator_supports_custom_starting_sequence() -> None:
    allocator = SequentialCompanyIdAllocator(
        starting_sequence=152,
    )

    identifier = await allocator.allocate()

    assert str(identifier) == "ACL-COM-00000152"


def test_allocator_rejects_invalid_starting_sequence() -> None:
    with pytest.raises(ValueError):
        SequentialCompanyIdAllocator(
            starting_sequence=0,
        )
