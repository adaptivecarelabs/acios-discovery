from abc import ABC, abstractmethod


class HttpClient(ABC):

    @abstractmethod
    async def get(
        self,
        url: str,
    ) -> str:
        """
        Download an HTML page.
        """
