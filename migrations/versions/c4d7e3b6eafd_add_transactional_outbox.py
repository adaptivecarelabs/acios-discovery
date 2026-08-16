"""
add transactional outbox

Revision ID: c4d7e3b6eafd
Revises: d3ccfdd8fac1
Create Date: 2026-08-15 03:59:36.844970

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c4d7e3b6eafd"
down_revision: str | None = "d3ccfdd8fac1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "outbox_events",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "event_type",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "aggregate_type",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "aggregate_id",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "payload",
            postgresql.JSONB,
            nullable=False,
        ),

        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        sa.Column(
            "last_error",
            sa.Text(),
            nullable=True,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_outbox_events_unpublished",
        "outbox_events",
        ["published_at", "created_at"],
    )

    op.create_index(
        "ix_outbox_events_event_type",
        "outbox_events",
        ["event_type"],
    )

    op.create_index(
        "ix_outbox_events_aggregate",
        "outbox_events",
        ["aggregate_type", "aggregate_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_outbox_events_aggregate",
        table_name="outbox_events",
    )

    op.drop_index(
        "ix_outbox_events_event_type",
        table_name="outbox_events",
    )

    op.drop_index(
        "ix_outbox_events_unpublished",
        table_name="outbox_events",
    )

    op.drop_table("outbox_events")
