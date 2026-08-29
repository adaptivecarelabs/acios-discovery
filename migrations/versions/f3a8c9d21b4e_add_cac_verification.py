"""add cac verification

Revision ID: f3a8c9d21b4e
Revises: a5903bd04114
Create Date: 2026-08-29 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f3a8c9d21b4e'
down_revision: str | Sequence[str] | None = 'a5903bd04114'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'companies',
        sa.Column('rc_number', sa.String(length=64), nullable=True),
    )
    op.add_column(
        'companies',
        sa.Column('entity_type', sa.String(length=32), nullable=True),
    )
    op.add_column(
        'companies',
        sa.Column(
            'registration_date',
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        'companies',
        sa.Column(
            'registration_status',
            sa.String(length=16),
            nullable=True,
        ),
    )
    op.add_column(
        'companies',
        sa.Column(
            'nature_of_business',
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.create_table(
        'cac_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'company_id',
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column('searched_name', sa.String(length=255), nullable=False),
        sa.Column('outcome', sa.String(length=16), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column(
            'matched_approved_name',
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column('matched_rc_number', sa.String(length=64), nullable=True),
        sa.Column(
            'matched_company_id',
            sa.Integer(),
            nullable=True,
        ),
        sa.Column('matched_entity_type', sa.String(length=32), nullable=True),
        sa.Column(
            'matched_registration_date',
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            'matched_registration_status',
            sa.String(length=16),
            nullable=True,
        ),
        sa.Column(
            'matched_nature_of_business',
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            'verified_at',
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_cac_verifications_company_id'),
        'cac_verifications',
        ['company_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_cac_verifications_outcome'),
        'cac_verifications',
        ['outcome'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_cac_verifications_outcome'),
        table_name='cac_verifications',
    )
    op.drop_index(
        op.f('ix_cac_verifications_company_id'),
        table_name='cac_verifications',
    )
    op.drop_table('cac_verifications')

    op.drop_column('companies', 'nature_of_business')
    op.drop_column('companies', 'registration_status')
    op.drop_column('companies', 'registration_date')
    op.drop_column('companies', 'entity_type')
    op.drop_column('companies', 'rc_number')
