from acios_discovery.domain.discovery import RawDiscovery
from acios_discovery.domain.http import HttpClient
from acios_discovery.infrastructure.connectors.finelib.detail_mapper import (
    FinelibDetailMapper,
)
from acios_discovery.infrastructure.connectors.finelib.detail_parser import (
    FinelibDetailParser,
)


class DiscoveryEnricher:
    """
    Downloads and enriches a discovered business
    using its detail page.
    """

    def __init__(
        self,
        http: HttpClient,
        parser: FinelibDetailParser,
        mapper: FinelibDetailMapper,
    ) -> None:

        self._http = http
        self._parser = parser
        self._mapper = mapper

    async def enrich(
        self,
        company: RawDiscovery,
    ) -> RawDiscovery:

        if not company.detail_url:
            return company

        html = await self._http.get(
            company.detail_url,
        )

        soup = self._parser.parse(
            html,
        )

        company.email = self._mapper.extract_email(
            soup,
        )

        company.website = self._mapper.extract_website(
            soup,
        )

        company.social_links = (
            self._mapper.extract_social_links(
                soup,
            )
        )

        company.year_founded = (
            self._mapper.extract_year_founded(
                soup,
            )
        )

        company.employee_count = (
            self._mapper.extract_employee_count(
                soup,
            )
        )

        company.business_locations = (
            self._mapper.extract_business_locations(
                soup,
            )
        )

        company.product_types = (
            self._mapper.extract_product_types(
                soup,
            )
        )

        company.payment_methods = (
            self._mapper.extract_payment_methods(
                soup,
            )
        )

        return company
