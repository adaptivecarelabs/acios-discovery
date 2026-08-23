"""add company id sequence

Revision ID: 54b23db840a1
Revises: b40f930e6bd3
Create Date: 2026-08-19 04:04:07.403941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54b23db840a1'
down_revision: Union[str, Sequence[str], None] = 'b40f930e6bd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE company_id_seq START WITH 1 INCREMENT BY 1",
    )


def downgrade() -> None:
    op.execute(
        "DROP SEQUENCE company_id_seq",
    )
