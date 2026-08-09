from __future__ import annotations

from abc import ABC, abstractmethod

from acios_discovery.domain.company.company import Company
from acios_discovery.domain.company.company_id import CompanyId


class CompanyRepository(ABC):
    """
    Repository for canonical Company aggregates.
    """

    @abstractmethod
    async def add(
        self,
        company: Company,
    ) -> None:
        """
        Persist a company.
        """

    @abstractmethod
    async def get(
        self,
        company_id: CompanyId,
    ) -> Company | None:
        """
        Retrieve a company by id.
        """

    @abstractmethod
    async def list_all(
        self,
    ) -> list[Company]:
        """
        Return all companies.
        """

    @abstractmethod
    async def count(
        self,
    ) -> int:
        """
        Number of companies.
        """

    @abstractmethod
    async def update(
        self,
        company: Company,
    ) -> None:
        """
        Persist modifications to an existing company.
        """


    #
    # Lookup API
    #

    @abstractmethod
    async def find_by_name(
        self,
        canonical_name: str,
    ) -> Company | None:
        """
        Find a company by its canonical name.
        """
        ...


    @abstractmethod
    async def find_by_alias(
        self,
        alias: str,
    ) -> Company | None:
        """
        Find a company by one of its aliases.
        """
        ...


    @abstractmethod
    async def find_by_phone(
        self,
        phone: str,
    ) -> Company | None:
        """
        Find a company by phone number.
        """
        ...


    @abstractmethod
    async def find_by_email(
        self,
        email: str,
    ) -> Company | None:
        """
        Find a company by email address.
        """
        ...


    @abstractmethod
    async def find_by_website(
        self,
        website: str,
    ) -> Company | None:
        """
        Find a company by website.
        """
        ...
