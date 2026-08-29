"""add outbox dead lettering

Revision ID: 8c6921290edf
Revises: 54b23db840a1
Create Date: 2026-08-21 00:47:53.646758

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8c6921290edf'
down_revision: str | Sequence[str] | None = '54b23db840a1'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "outbox_events",
        sa.Column(
            "dead_lettered_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("outbox_events", "dead_lettered_at")
