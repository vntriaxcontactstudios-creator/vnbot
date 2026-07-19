"""VNBOT API — Audit / Activity endpoints.

GET /api/v1/operations       — list operations (paginated, filterable)
GET /api/v1/operations/{id}   — get single operation with full details
GET /api/v1/activity/summary  — summary stats (counts by status, type)

Per docs/08 §16 (Audit log structure) + docs/03 §17 (ExecutionLog):
- Operations track the lifecycle of every user/agent-initiated action
- ExecutionLogs track tool calls + agent actions
- Never log plaintext/audio/secrets — only input_hash + result_summary_ciphertext
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_workspace_id
from ...infrastructure.db.models import ExecutionLog, Operation
from ...infrastructure.db.session import get_db
from ...schemas.audit import (
    ActivitySummaryResponse,
    ExecutionLogResponse,
    OperationListResponse,
    OperationResponse,
    OperationStatusFilter,
)

router = APIRouter(tags=["audit"])

DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"


def _serialize_operation(op: Operation) -> OperationResponse:
    """Convert Operation ORM to response model."""
    return OperationResponse(
        id=op.id,
        workspace_id=op.workspace_id,
        user_id=op.user_id,
        agent_id=op.agent_id,
        conversation_id=op.conversation_id,
        type=op.type,
        status=op.status,
        risk_level=op.risk_level,
        input_ref=op.input_ref,  # SHA-256 hash, safe to expose
        proposal_json=op.proposal_json or {},
        requires_confirmation=op.requires_confirmation,
        confirmed_at=op.confirmed_at,
        expires_at=op.expires_at,
        idempotency_key=op.idempotency_key,
        created_at=op.created_at,
        updated_at=op.updated_at,
    )


def _serialize_execution_log(log: ExecutionLog) -> ExecutionLogResponse:
    """Convert ExecutionLog ORM to response model."""
    return ExecutionLogResponse(
        id=log.id,
        workspace_id=log.workspace_id,
        operation_id=log.operation_id,
        agent_id=log.agent_id,
        integration_id=log.integration_id,
        tool_name=log.tool_name,
        status=log.status,
        duration_ms=log.duration_ms,
        error_code=log.error_code,
        input_hash=log.input_hash,  # SHA-256 hash, safe
        result_summary=log.result_summary_ciphertext,  # ciphertext, safe
        created_at=log.created_at,
    )


@router.get("/operations", response_model=OperationListResponse)
async def list_operations(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status_filter: OperationStatusFilter | None = Query(default=None, alias="status"),
    type_filter: str | None = Query(default=None, alias="type"),
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> OperationListResponse:
    """List operations (paginated, most recent first)."""
    stmt = select(Operation).where(Operation.workspace_id == DEFAULT_WORKSPACE_ID)

    if status_filter:
        stmt = stmt.where(Operation.status == status_filter.value)
    if type_filter:
        stmt = stmt.where(Operation.type == type_filter)

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    stmt = stmt.order_by(Operation.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    ops = result.scalars().all()

    return OperationListResponse(
        items=[_serialize_operation(op) for op in ops],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/operations/{operation_id}", response_model=OperationResponse)
async def get_operation(
    operation_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> OperationResponse:
    """Get a single operation by ID."""
    op = await db.get(Operation, operation_id)
    if op is None or op.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operation {operation_id} not found",
        )
    return _serialize_operation(op)


@router.get("/activity/summary", response_model=ActivitySummaryResponse)
async def get_activity_summary(
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ActivitySummaryResponse:
    """Summary stats: counts by status, type, and recent activity."""
    # Count by status
    status_stmt = (
        select(Operation.status, func.count())
        .where(Operation.workspace_id == DEFAULT_WORKSPACE_ID)
        .group_by(Operation.status)
    )
    status_counts = dict((await db.execute(status_stmt)).all())

    # Count by type
    type_stmt = (
        select(Operation.type, func.count())
        .where(Operation.workspace_id == DEFAULT_WORKSPACE_ID)
        .group_by(Operation.type)
    )
    type_counts = dict((await db.execute(type_stmt)).all())

    # Total count
    total = sum(status_counts.values())

    # Recent operations (last 5)
    recent_stmt = (
        select(Operation)
        .where(Operation.workspace_id == DEFAULT_WORKSPACE_ID)
        .order_by(Operation.created_at.desc())
        .limit(5)
    )
    recent_ops = (await db.execute(recent_stmt)).scalars().all()

    return ActivitySummaryResponse(
        total_operations=total,
        status_counts=status_counts,
        type_counts=type_counts,
        recent_operations=[_serialize_operation(op) for op in recent_ops],
        generated_at=datetime.now(timezone.utc),
    )
