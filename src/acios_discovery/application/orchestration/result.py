from dataclasses import dataclass


@dataclass(slots=True)
class DiscoveryOrchestrationResult:
    state: str

    city: str

    category_slug: str

    pages_crawled: int

    companies_discovered: int
