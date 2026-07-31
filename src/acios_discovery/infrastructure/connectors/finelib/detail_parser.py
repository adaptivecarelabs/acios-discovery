from bs4 import BeautifulSoup


class FinelibDetailParser:
    """
    Parses one Finelib business
    detail page.
    """

    def parse(
        self,
        html: str,
    ) -> BeautifulSoup:
        return BeautifulSoup(
            html,
            "html.parser",
        )
