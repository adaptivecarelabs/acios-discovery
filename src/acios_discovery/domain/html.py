from abc import ABC, abstractmethod


class HtmlClient(ABC):

    @abstractmethod
    async def get(
        self,
        url: str,
    ) -> str:
        """
        Download HTML from a URL.
        """
