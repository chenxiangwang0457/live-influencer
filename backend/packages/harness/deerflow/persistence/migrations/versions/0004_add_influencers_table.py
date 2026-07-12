"""add influencers table.

Revision ID: 0004_add_influencers_table
Revises: 0003_scheduled_tasks
Create Date: 2026-07-12
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_add_influencers_table"
down_revision: str | Sequence[str] | None = "0003_scheduled_tasks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "influencers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("platform_uid", sa.String(length=128), nullable=False),
        sa.Column("nickname", sa.String(length=128), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("sub_categories", sa.JSON(), nullable=True),
        sa.Column("followers_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_comments", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_shares", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("engagement_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("avg_gmv", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("avg_sales", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price_range_min", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price_range_max", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("demographics", sa.JSON(), nullable=True),
        sa.Column("content_style", sa.JSON(), nullable=True),
        sa.Column("brand_history", sa.JSON(), nullable=True),
        sa.Column("data_source", sa.String(length=32), nullable=False, server_default="mock"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("influencers", schema=None) as batch_op:
        batch_op.create_index("ix_influencers_platform", ["platform"], unique=False)
        batch_op.create_index("ix_influencers_platform_uid", ["platform_uid"], unique=False)
        batch_op.create_index("ix_influencers_category", ["category"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("influencers", schema=None) as batch_op:
        batch_op.drop_index("ix_influencers_platform")
        batch_op.drop_index("ix_influencers_platform_uid")
        batch_op.drop_index("ix_influencers_category")
    op.drop_table("influencers")
