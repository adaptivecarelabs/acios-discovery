"""add users table

Revision ID: f77b85e7b1b0
Revises: 34a469cb126f
Create Date: 2026-08-24 23:14:02.423250

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f77b85e7b1b0'
down_revision: str | Sequence[str] | None = '34a469cb126f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='member'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name='users_pkey'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index(
        'ix_users_email',
        'users',
        ['email'],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
