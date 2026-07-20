"""add skills + learning_logs tables (Hermes ADR-0009 Fase 0.7)

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-20
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create skills + learning_logs tables for Hermes learning loop.

    Per ADR-0009:
    - skills: markdown bodies + trigger metadata, versioned, with confidence
    - learning_logs: audit trail of every Hermes action (no silent mutations)
    """
    # ─── skills ───
    op.create_table(
        "skills",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("body_markdown", sa.Text, nullable=False, server_default=""),
        sa.Column("triggers_json", sa.JSON, server_default="{}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("origin", sa.String(20), nullable=False, server_default="user"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.3"),
        sa.Column("use_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tags_ciphertext", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_skills_workspace_id", "skills", ["workspace_id"])
    op.create_index("ix_skills_name", "skills", ["name"])
    op.create_index("ix_skills_status", "skills", ["status"])
    op.create_index("ix_skills_created_at", "skills", ["created_at"])
    # Note: unique constraint on (workspace_id, name) omitted for SQLite compat
    # — enforced at application layer in skills.py create_skill endpoint

    # ─── learning_logs ───
    op.create_table(
        "learning_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("origin", sa.String(20), nullable=False, server_default="hermes"),
        sa.Column("trigger_reason", sa.String(255), nullable=True),
        sa.Column("review_json", sa.JSON, server_default="{}"),
        sa.Column("outcome_summary", sa.Text, nullable=False, server_default=""),
        sa.Column("memory_ids_json", sa.JSON, server_default="[]"),
        sa.Column("skill_id", sa.String(36), sa.ForeignKey("skills.id"), nullable=True),
        sa.Column("llm_model", sa.String(100), nullable=True),
        sa.Column("llm_tokens_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("success", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_learning_logs_workspace_id", "learning_logs", ["workspace_id"])
    op.create_index("ix_learning_logs_action", "learning_logs", ["action"])
    op.create_index("ix_learning_logs_success", "learning_logs", ["success"])
    op.create_index("ix_learning_logs_created_at", "learning_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("learning_logs")
    op.drop_table("skills")
