from acios_discovery.domain.company.company_repository import (
    CompanyRepository,
)


def test_company_repository_is_abstract():

    assert hasattr(
        CompanyRepository,
        "add",
    )

    assert hasattr(
        CompanyRepository,
        "get",
    )

    assert hasattr(
        CompanyRepository,
        "list_all",
    )

    assert hasattr(
        CompanyRepository,
        "count",
    )

    assert hasattr(
        CompanyRepository,
        "update",
    )
