"""VNBOT API — Pydantic v2 request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────────────────
# Chat endpoints
# ──────────────────────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    """POST /chat — parse user input and return an operation proposal."""

    text: str = Field(..., min_length=1, max_length=10_000, description="User input text")
    conversation_id: str | None = Field(default=None, description="Optional conversation ID")
    timezone: str = Field(default="UTC", description="User IANA timezone")
    idempotency_key: str | None = Field(
        default=None, description="Optional idempotency key for safe retries"
    )


class ProposalReminder(BaseModel):
    """Reminder proposal extracted from user input."""

    title: str
    due_at: datetime
    timezone: str
    recurrence_frequency: str = "none"
    recurrence_interval: int = 1
    priority: str = "normal"
    channel: str = "mock"
    confidence: float = Field(ge=0.0, le=1.0)


class ProposalMemory(BaseModel):
    """Memory proposal extracted from user input."""

    content: str
    memory_type: str = "note"
    tags: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """Response from POST /chat.

    If parse succeeded and confidence is high, returns operation_id + proposal.
    User must confirm via POST /chat/operations/{id}/confirm.
    If parse failed, returns error + suggestion for LLM escalation.
    """

    operation_id: str
    intent: str
    parsed: bool
    confidence: float = Field(ge=0.0, le=1.0)
    proposal_reminder: ProposalReminder | None = None
    proposal_memory: ProposalMemory | None = None
    requires_confirmation: bool = True
    expires_at: datetime | None = None
    notes: list[str] = Field(default_factory=list)
    error: str | None = None
    suggestion: str | None = None


class ConfirmRequest(BaseModel):
    """POST /chat/operations/{id}/confirm — confirm a proposed operation."""

    idempotency_key: str | None = None
    edits: dict[str, Any] | None = Field(
        default=None,
        description="Optional edits to the proposal (e.g. override title, due_at)",
    )


class ConfirmResponse(BaseModel):
    """Response from confirm endpoint."""

    operation_id: str
    status: str
    entity_id: str | None = None  # created reminder/memory ID
    entity_type: str | None = None  # "reminder" | "memory" | "list_item"
    next_due_at: datetime | None = None
    error: str | None = None


# ──────────────────────────────────────────────────────────────────────────────
# Health endpoints
# ──────────────────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "down"]
    version: str
    timestamp: datetime
    checks: dict[str, str] = Field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# Generic error response
# ──────────────────────────────────────────────────────────────────────────────


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    request_id: str | None = None
