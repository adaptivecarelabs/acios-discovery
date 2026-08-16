from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from acios_discovery.application.discovery.pipeline import (
    DiscoveryPipeline,
)

from .discovery_services import DiscoveryServices


def build_pipeline(
    session: AsyncSession,
) -> DiscoveryPipeline:
    """
    Build the complete Discovery Pipeline.

    The supplied AsyncSession is shared by every
    persistence repository used by the pipeline.
    """

    services = DiscoveryServices(
        session=session,
    )

    return DiscoveryPipeline(
        crawler=services.crawl_engine,
        enricher=services.enrichment_engine,
        persistence=services.persistence,
        processor=services.batch_processor,
    )
