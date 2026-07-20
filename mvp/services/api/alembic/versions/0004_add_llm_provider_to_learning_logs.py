"""add llm_provider column to learning_logs (cost tracking ADR-0012)

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-20
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add llm_provider column for cost tracking per provider.

    Per ADR-0012: track which provider served each request so we can compute
    per-provider token usage and cost.
    """
    op.add_column(
        "learning_logs",
        sa.Column("llm_provider", sa.String(20), nullable=True),
    )
    op.create_index("ix_learning_logs_llm_provider", "learning_logs", ["llm_provider"])


def downgrade() -> None:
    op.drop_index("ix_learning_logs_llm_provider", table_name="learning_logs")
    op.drop_column("learning_logs", "llm_provider")
