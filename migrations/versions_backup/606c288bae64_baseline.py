"""baseline

Revision ID: 606c288bae64
Revises:
Create Date: 2026-08-11 18:30:06.934374

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '606c288bae64'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
