import pytest

from acios_discovery.application.enrichment.finelib_enricher import (
    FinelibEnricher,
)
from acios_discovery.infrastructure.connectors.finelib.detail_mapper import (
    FinelibDetailMapper,
)
from acios_discovery.infrastructure.connectors.finelib.detail_parser import (
    FinelibDetailParser,
)
from tests.fakes.test_html_client import FakeHttpClient


@pytest.mark.asyncio
async def test_returns_record_when_detail_url_missing(
    sample_discovery_record,
):

    sample_discovery_record.company.detail_url = None

    enricher = FinelibEnricher(
        http=FakeHttpClient({}),
        parser=FinelibDetailParser(),
        mapper=FinelibDetailMapper(),
    )

    result = await enricher.enrich(
        sample_discovery_record,
    )

    assert result is sample_discovery_record


@pytest.mark.asyncio
async def test_enriches_company_from_detail_page(
    sample_discovery_record,
):

    html = """
    <html>
        <body>

            <a href="mailto:info@example.com">
                info@example.com
            </a>

            <div class="cmpny-lstng url">
                <a href="https://example.com">
                    https://example.com
                </a>
            </div>

        </body>
    </html>    
"""

    sample_discovery_record.company.detail_url = (
        "https://example.com/company"
    )

    http = FakeHttpClient(
        {
            "https://example.com/company": html,
        }
    )

    enricher = FinelibEnricher(
        http=http,
        parser=FinelibDetailParser(),
        mapper=FinelibDetailMapper(),
    )

    result = await enricher.enrich(
        sample_discovery_record,
    )

    assert result.company.email == "info@example.com"
    assert result.company.website == "https://example.com"
