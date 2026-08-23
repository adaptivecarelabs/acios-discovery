from __future__ import annotations

from sqlalchemy import Sequence

from acios_discovery.infrastructure.persistence.metadata import Base

#
# Registered against Base.metadata so both Base.metadata.create_all()
# (used by the test suite's per-worker schema setup) and Alembic
# autogenerate see this sequence consistently.
#

company_id_sequence = Sequence(
    "company_id_seq",
    metadata=Base.metadata,
)
