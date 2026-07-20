"""VNBOT API — SQLAlchemy models.

Maps domain entities to DB tables. Uses SQLAlchemy 2 declarative style.

Sync fields (version, updated_at, deleted_at) are present from day 1 per ADR-0005,
even though sync is not implemented in 0.1 — useful for audit/export.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vnbot_domain.entities.common import Authority, Provenance, Sensitivity, OperationStatus, RiskTier
from vnbot_domain.entities.reminders import (
    OccurrenceStatus,
    RecurrenceFrequency,
    ReminderChannel,
    ReminderPriority,
    ReminderStatus,
)
from .session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ──────────────────────────────────────────────────────────────────────────────
# User & Workspace (minimal for 0.1 — single-user local mode)
# ──────────────────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False, default="User")
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    locale: Mapped[str] = mapped_column(String(10), nullable=False, default="es")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Personal")
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="personal")
    default_timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    settings_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


# ──────────────────────────────────────────────────────────────────────────────
# Memory (simplified for 0.1 — full schema in 0.5)
# ──────────────────────────────────────────────────────────────────────────────


class MemoryNode(Base):
    __tablename__ = "memory_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="note")
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    content_ciphertext: Mapped[str] = mapped_column(Text, nullable=True)
    content_format: Mapped[str] = mapped_column(String(20), nullable=False, default="text")
    structured_data_ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="explicit_user_input")
    provenance: Mapped[str] = mapped_column(SAEnum(Provenance), nullable=False, default=Provenance.EXPLICIT_USER_INPUT)
    authority: Mapped[str] = mapped_column(SAEnum(Authority), nullable=False, default=Authority.EXPLICIT)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    sensitivity: Mapped[str] = mapped_column(SAEnum(Sensitivity), nullable=False, default=Sensitivity.PERSONAL)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MemoryEdge(Base):
    __tablename__ = "memory_edges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    source_node_id: Mapped[str] = mapped_column(ForeignKey("memory_nodes.id"), nullable=False, index=True)
    target_node_id: Mapped[str] = mapped_column(ForeignKey("memory_nodes.id"), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    properties_ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance: Mapped[str] = mapped_column(SAEnum(Provenance), nullable=False, default=Provenance.EXPLICIT_USER_INPUT)
    authority: Mapped[str] = mapped_column(SAEnum(Authority), nullable=False, default=Authority.EXPLICIT)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ──────────────────────────────────────────────────────────────────────────────
# Reminders & Occurrences
# ──────────────────────────────────────────────────────────────────────────────


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description_ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    recurrence_frequency: Mapped[str] = mapped_column(
        SAEnum(RecurrenceFrequency), nullable=False, default=RecurrenceFrequency.NONE
    )
    recurrence_interval: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    recurrence_by_weekdays: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recurrence_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recurrence_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recurrence_rule_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    priority: Mapped[str] = mapped_column(SAEnum(ReminderPriority), nullable=False, default=ReminderPriority.NORMAL)
    channel: Mapped[str] = mapped_column(SAEnum(ReminderChannel), nullable=False, default=ReminderChannel.MOCK)
    recipient_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(SAEnum(ReminderStatus), nullable=False, default=ReminderStatus.ACTIVE, index=True)
    source_memory_id: Mapped[str | None] = mapped_column(ForeignKey("memory_nodes.id"), nullable=True)
    next_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    provenance: Mapped[str] = mapped_column(SAEnum(Provenance), nullable=False, default=Provenance.EXPLICIT_USER_INPUT)
    authority: Mapped[str] = mapped_column(SAEnum(Authority), nullable=False, default=Authority.EXPLICIT)
    sensitivity: Mapped[str] = mapped_column(SAEnum(Sensitivity), nullable=False, default=Sensitivity.PERSONAL)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)


class ReminderOccurrence(Base):
    __tablename__ = "reminder_occurrences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    reminder_id: Mapped[str] = mapped_column(ForeignKey("reminders.id"), nullable=False, index=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    occurrence_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    status: Mapped[str] = mapped_column(
        SAEnum(OccurrenceStatus), nullable=False, default=OccurrenceStatus.PENDING, index=True
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


# ──────────────────────────────────────────────────────────────────────────────
# Operation & ExecutionLog (audit)
# ──────────────────────────────────────────────────────────────────────────────


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    agent_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    conversation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(SAEnum(OperationStatus), nullable=False, default=OperationStatus.RECEIVED)
    risk_level: Mapped[str] = mapped_column(SAEnum(RiskTier), nullable=False, default=RiskTier.LOW)
    input_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    proposal_json: Mapped[dict] = mapped_column(JSON, default=dict)
    requires_confirmation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    operation_id: Mapped[str | None] = mapped_column(ForeignKey("operations.id"), nullable=True)
    agent_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    integration_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tool_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256
    result_summary_ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


# ──────────────────────────────────────────────────────────────────────────────
# Notifications (mock channel for 0.1)
# ──────────────────────────────────────────────────────────────────────────────


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    occurrence_id: Mapped[str | None] = mapped_column(ForeignKey("reminder_occurrences.id"), nullable=True)
    channel: Mapped[str] = mapped_column(String(20), nullable=False, default="mock")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body_ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class List(Base):
    __tablename__ = "lists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description_ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class ListItem(Base):
    __tablename__ = "list_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    list_id: Mapped[str] = mapped_column(ForeignKey("lists.id"), nullable=False, index=True)
    title_ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
