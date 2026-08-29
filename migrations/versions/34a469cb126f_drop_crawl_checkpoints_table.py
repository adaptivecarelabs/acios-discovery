"""drop crawl_checkpoints table

Revision ID: 34a469cb126f
Revises: 8c6921290edf
Create Date: 2026-08-23 20:43:49.850502

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '34a469cb126f'
down_revision: str | Sequence[str] | None = '8c6921290edf'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('crawl_checkpoints')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        'crawl_checkpoints',
        sa.Column('session_id', sa.String(length=50), nullable=False),
        sa.Column('state', sa.String(length=120), nullable=False),
        sa.Column('city', sa.String(length=120), nullable=False),
        sa.Column('category_slug', sa.String(length=255), nullable=False),
        sa.Column('page', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('company_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('session_id', name='crawl_checkpoints_pkey'),
    )
