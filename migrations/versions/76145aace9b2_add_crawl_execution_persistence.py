"""
add crawl execution persistence

Revision ID: 76145aace9b2
Revises: c4d7e3b6eafd
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "76145aace9b2"
down_revision: str | Sequence[str] | None = "c4d7e3b6eafd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "crawl_sessions",
        sa.Column(
            "id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "finished_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "jobs_total",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "jobs_completed",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "jobs_failed",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "retries",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "pages_crawled",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "companies_discovered",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_crawl_sessions_status",
        "crawl_sessions",
        ["status"],
    )

    op.create_table(
        "crawl_jobs",
        sa.Column(
            "id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "listing_url",
            sa.String(length=1000),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "city",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "category_slug",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "page",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "priority",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),
        sa.Column(
            "retries",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "max_retries",
            sa.Integer(),
            nullable=False,
            server_default="3",
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "last_completed_page",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "total_pages",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "heartbeat_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "lease_until",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "last_error",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["crawl_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id",
            "source",
            "state",
            "city",
            "category_slug",
            name="uq_crawl_jobs_session_plan",
        ),
    )

    op.create_index(
        "ix_crawl_jobs_session_id",
        "crawl_jobs",
        ["session_id"],
    )

    op.create_index(
        "ix_crawl_jobs_source",
        "crawl_jobs",
        ["source"],
    )

    op.create_index(
        "ix_crawl_jobs_priority",
        "crawl_jobs",
        ["priority"],
    )

    op.create_index(
        "ix_crawl_jobs_status",
        "crawl_jobs",
        ["status"],
    )

    op.create_table(
        "crawl_checkpoints",
        sa.Column(
            "session_id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "city",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "category_slug",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "page",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "company_index",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("session_id"),
    )


def downgrade() -> None:
    op.drop_table("crawl_checkpoints")

    op.drop_index(
        "ix_crawl_jobs_status",
        table_name="crawl_jobs",
    )

    op.drop_index(
        "ix_crawl_jobs_priority",
        table_name="crawl_jobs",
    )

    op.drop_index(
        "ix_crawl_jobs_source",
        table_name="crawl_jobs",
    )

    op.drop_index(
        "ix_crawl_jobs_session_id",
        table_name="crawl_jobs",
    )

    op.drop_table("crawl_jobs")

    op.drop_index(
        "ix_crawl_sessions_status",
        table_name="crawl_sessions",
    )

    op.drop_table("crawl_sessions")
