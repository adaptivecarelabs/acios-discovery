from acios_discovery.domain.connectors import (
    BaseConnector,
)


class DummyConnector(BaseConnector):
    
    async def crawl(self):
        return []

    def has_next_page(
        self,
        html: str,
    ) -> bool:
        return False


def test_connector_contract() -> None:
    connector = DummyConnector()

    assert isinstance(
        connector,
        BaseConnector,
    )
