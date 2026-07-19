"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-19
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── users ───
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("display_name", sa.String(255), nullable=False, server_default="User"),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("locale", sa.String(10), nullable=False, server_default="es"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ─── workspaces ───
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, server_default="Personal"),
        sa.Column("type", sa.String(20), nullable=False, server_default="personal"),
        sa.Column("default_timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("settings_json", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ─── memory_nodes ───
    op.create_table(
        "memory_nodes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="note"),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("content_ciphertext", sa.Text, nullable=True),
        sa.Column("content_format", sa.String(20), nullable=False, server_default="text"),
        sa.Column("structured_data_ciphertext", sa.Text, nullable=True),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="explicit_user_input"),
        sa.Column("provenance", sa.String(50), nullable=False, server_default="explicit_user_input"),
        sa.Column("authority", sa.String(50), nullable=False, server_default="explicit"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("sensitivity", sa.String(50), nullable=False, server_default="personal"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("device_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_memory_nodes_workspace", "memory_nodes", ["workspace_id"])
    op.create_index("ix_memory_nodes_workspace_type_status", "memory_nodes", ["workspace_id", "type", "status"])
    op.create_index("ix_memory_nodes_workspace_created", "memory_nodes", ["workspace_id", "created_at"])
    op.create_index("ix_memory_nodes_workspace_sensitivity", "memory_nodes", ["workspace_id", "sensitivity"])

    # ─── memory_edges ───
    op.create_table(
        "memory_edges",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("source_node_id", sa.String(36), sa.ForeignKey("memory_nodes.id"), nullable=False),
        sa.Column("target_node_id", sa.String(36), sa.ForeignKey("memory_nodes.id"), nullable=False),
        sa.Column("relation_type", sa.String(50), nullable=False),
        sa.Column("properties_ciphertext", sa.Text, nullable=True),
        sa.Column("provenance", sa.String(50), nullable=False, server_default="explicit_user_input"),
        sa.Column("authority", sa.String(50), nullable=False, server_default="explicit"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_memory_edges_workspace", "memory_edges", ["workspace_id"])
    op.create_index("ix_memory_edges_workspace_source", "memory_edges", ["workspace_id", "source_node_id"])
    op.create_index("ix_memory_edges_workspace_target", "memory_edges", ["workspace_id", "target_node_id"])

    # ─── reminders ───
    op.create_table(
        "reminders",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("created_by_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description_ciphertext", sa.Text, nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("recurrence_frequency", sa.String(20), nullable=False, server_default="none"),
        sa.Column("recurrence_interval", sa.Integer, nullable=False, server_default="1"),
        sa.Column("recurrence_by_weekdays", sa.String(50), nullable=True),
        sa.Column("recurrence_count", sa.Integer, nullable=True),
        sa.Column("recurrence_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recurrence_rule_version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("channel", sa.String(20), nullable=False, server_default="mock"),
        sa.Column("recipient_ref", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("source_memory_id", sa.String(36), sa.ForeignKey("memory_nodes.id"), nullable=True),
        sa.Column("next_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provenance", sa.String(50), nullable=False, server_default="explicit_user_input"),
        sa.Column("authority", sa.String(50), nullable=False, server_default="explicit"),
        sa.Column("sensitivity", sa.String(50), nullable=False, server_default="personal"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("device_id", sa.String(100), nullable=True),
    )
    op.create_index("ix_reminders_workspace_status_next_due", "reminders", ["workspace_id", "status", "next_due_at"])

    # ─── reminder_occurrences ───
    op.create_table(
        "reminder_occurrences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("reminder_id", sa.String(36), sa.ForeignKey("reminders.id"), nullable=False),
        sa.Column("workspace_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("occurrence_key", sa.String(255), nullable=False, unique=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reminder_occurrences_reminder", "reminder_occurrences", ["reminder_id"])
    op.create_index("ix_reminder_occurrences_workspace", "reminder_occurrences", ["workspace_id"])
    op.create_index("ix_reminder_occurrences_key", "reminder_occurrences", ["occurrence_key"], unique=True)
    op.create_index("ix_reminder_occurrences_status_due", "reminder_occurrences", ["status", "due_at"])

    # ─── operations ───
    op.create_table(
        "operations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("agent_id", sa.String(100), nullable=True),
        sa.Column("conversation_id", sa.String(36), nullable=True),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="received"),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="low"),
        sa.Column("input_ref", sa.String(500), nullable=True),
        sa.Column("proposal_json", sa.JSON, server_default="{}"),
        sa.Column("requires_confirmation", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_operations_workspace_status_created", "operations", ["workspace_id", "status", "created_at"])
    op.create_index("ix_operations_idempotency", "operations", ["idempotency_key"])

    # ─── execution_logs ───
    op.create_table(
        "execution_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("operation_id", sa.String(36), sa.ForeignKey("operations.id"), nullable=True),
        sa.Column("agent_id", sa.String(100), nullable=True),
        sa.Column("integration_id", sa.String(100), nullable=True),
        sa.Column("tool_name", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("input_hash", sa.String(64), nullable=True),
        sa.Column("result_summary_ciphertext", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_execution_logs_workspace_created", "execution_logs", ["workspace_id", "created_at"])

    # ─── notifications ───
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("occurrence_id", sa.String(36), sa.ForeignKey("reminder_occurrences.id"), nullable=True),
        sa.Column("channel", sa.String(20), nullable=False, server_default="mock"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body_ciphertext", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_workspace_status_created", "notifications", ["workspace_id", "status", "created_at"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("execution_logs")
    op.drop_table("operations")
    op.drop_table("reminder_occurrences")
    op.drop_table("reminders")
    op.drop_table("memory_edges")
    op.drop_table("memory_nodes")
    op.drop_table("workspaces")
    op.drop_table("users")
