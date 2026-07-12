"""add selections, feedbacks, influencer_scores tables.

Revision ID: 0005_add_selections_feedbacks_influencer_scores_tables
Revises: 0004_add_influencers_table
Create Date: 2026-07-12
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_add_selections_feedbacks_influencer_scores_tables"
down_revision: str | Sequence[str] | None = "0004_add_influencers_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- selections ---
    op.create_table(
        "selections",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("thread_id", sa.String(length=128), nullable=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("goal", sa.Text(), nullable=True),
        sa.Column("criteria", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("selections", schema=None) as batch_op:
        batch_op.create_index("ix_selections_thread_id", ["thread_id"], unique=False)
        batch_op.create_index("ix_selections_status", ["status"], unique=False)

    # --- selection_influencers ---
    op.create_table(
        "selection_influencers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("selection_id", sa.String(length=36), nullable=False),
        sa.Column("influencer_id", sa.String(length=36), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("match_reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="shortlisted"),
        sa.Column("added_by", sa.String(length=32), nullable=False, server_default="ai_recommend"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["selection_id"], ["selections.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["influencer_id"], ["influencers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- feedbacks ---
    op.create_table(
        "feedbacks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("selection_id", sa.String(length=36), nullable=True),
        sa.Column("influencer_id", sa.String(length=36), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review", sa.Text(), nullable=True),
        sa.Column("sales_performance", sa.JSON(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["selection_id"], ["selections.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["influencer_id"], ["influencers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("feedbacks", schema=None) as batch_op:
        batch_op.create_index("ix_feedbacks_influencer_id", ["influencer_id"], unique=False)

    # --- influencer_scores ---
    op.create_table(
        "influencer_scores",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("influencer_id", sa.String(length=36), nullable=False),
        sa.Column("dimension", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("factors", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["influencer_id"], ["influencers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("influencer_scores", schema=None) as batch_op:
        batch_op.create_index("ix_influencer_scores_influencer_id", ["influencer_id"], unique=False)


def downgrade() -> None:
    # Drop in reverse order of creation (respect FK constraints)
    with op.batch_alter_table("influencer_scores", schema=None) as batch_op:
        batch_op.drop_index("ix_influencer_scores_influencer_id")
    op.drop_table("influencer_scores")

    with op.batch_alter_table("feedbacks", schema=None) as batch_op:
        batch_op.drop_index("ix_feedbacks_influencer_id")
    op.drop_table("feedbacks")

    op.drop_table("selection_influencers")

    with op.batch_alter_table("selections", schema=None) as batch_op:
        batch_op.drop_index("ix_selections_thread_id")
        batch_op.drop_index("ix_selections_status")
    op.drop_table("selections")
