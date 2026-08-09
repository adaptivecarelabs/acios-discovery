from __future__ import annotations

from acios_discovery.application.discovery.pipeline import (
    DiscoveryPipeline,
)

from .discovery_services import DiscoveryServices


def build_pipeline() -> DiscoveryPipeline:
    """
    Build the complete Discovery Pipeline.

    This is the application's Composition Root.
    """

    services = DiscoveryServices()

    return DiscoveryPipeline(
        crawler=services.crawl_engine,
        enricher=services.enrichment_engine,
        processor=services.batch_processor,
    )
