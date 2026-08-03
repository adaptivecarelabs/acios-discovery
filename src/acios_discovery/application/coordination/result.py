from dataclasses import dataclass


@dataclass(slots=True)
class CrawlCoordinatorResult:
    """
    Summary returned by the crawl coordinator.
    """

    states: int

    cities: int

    categories: int

    crawl_runs: int

    companies_discovered: int
