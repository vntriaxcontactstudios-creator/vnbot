"""VNBOT API — Audit schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class OperationStatusFilter(str, Enum):
    """Filter values for operation status."""

    RECEIVED = "received"
    CLASSIFYING = "classifying"
    PROPOSED = "proposed"
    NEEDS_CLARIFICATION = "needs_clarification"
    WAITING_CONFIRMATION = "waiting_confirmation"
    QUEUED = "queued"
    EXECUTING = "executing"
    RETRYING = "retrying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class OperationResponse(BaseModel):
    """Operation as returned by the API."""

    id: str
    workspace_id: str
    user_id: str | None
    agent_id: str | None
    conversation_id: str | None
    type: str
    status: str
    risk_level: str
    input_ref: str | None  # SHA-256 hash, safe to expose
    proposal_json: dict[str, Any]
    requires_confirmation: bool
    confirmed_at: datetime | None
    expires_at: datetime | None
    idempotency_key: str | None
    created_at: datetime
    updated_at: datetime


class OperationListResponse(BaseModel):
    """Paginated list of operations."""

    items: list[OperationResponse]
    total: int
    limit: int
    offset: int


class ExecutionLogResponse(BaseModel):
    """Execution log entry."""

    id: str
    workspace_id: str
    operation_id: str | None
    agent_id: str | None
    integration_id: str | None
    tool_name: str | None
    status: str
    duration_ms: int | None
    error_code: str | None
    input_hash: str | None  # SHA-256, safe
    result_summary: str | None  # ciphertext
    created_at: datetime


class ActivitySummaryResponse(BaseModel):
    """Summary stats for the activity panel."""

    total_operations: int
    status_counts: dict[str, int]
    type_counts: dict[str, int]
    recent_operations: list[OperationResponse]
    generated_at: datetime
