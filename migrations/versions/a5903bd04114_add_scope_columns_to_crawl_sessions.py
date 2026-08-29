"""add scope columns to crawl_sessions

Revision ID: a5903bd04114
Revises: f77b85e7b1b0
Create Date: 2026-08-24 23:37:38.078902

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

# revision identifiers, used by Alembic.
revision: str = 'a5903bd04114'
down_revision: str | Sequence[str] | None = 'f77b85e7b1b0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('crawl_sessions', sa.Column('state', sa.String(length=120), nullable=True))
    op.add_column('crawl_sessions', sa.Column('categories', ARRAY(sa.String(length=255)), nullable=True))
    op.add_column('crawl_sessions', sa.Column('max_jobs', sa.Integer(), nullable=True))
    op.add_column('crawl_sessions', sa.Column('triggered_by_user_id', sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('crawl_sessions', 'triggered_by_user_id')
    op.drop_column('crawl_sessions', 'max_jobs')
    op.drop_column('crawl_sessions', 'categories')
    op.drop_column('crawl_sessions', 'state')
