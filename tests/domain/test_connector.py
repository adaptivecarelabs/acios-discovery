from acios_discovery.domain.connectors import (
    BaseConnector,
)
from acios_discovery.domain.crawling.job import CrawlJob
from acios_discovery.domain.discovery import DiscoveryRecord


class DummyConnector(BaseConnector):
    
    async def crawl(
            self,
            job: CrawlJob,
        ) -> list [DiscoveryRecord]:
        return []

    def next_page_url(
        self,
        html: str,
        current_url: str,
    ) -> str | None:
        return None


def test_connector_contract() -> None:
    connector = DummyConnector()

    assert isinstance(
        connector,
        BaseConnector,
    )
