"""VNBOT API — Reminders endpoints.

GET    /api/v1/reminders          — list reminders (filterable by status)
GET    /api/v1/reminders/{id}      — get single reminder
POST   /api/v1/reminders/{id}/complete — mark reminder as completed
POST   /api/v1/reminders/{id}/snooze   — snooze reminder
POST   /api/v1/reminders/{id}/cancel   — cancel reminder
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from vnbot_domain.entities.reminders import ReminderStatus
from ...dependencies import get_workspace_id
from ...infrastructure.db.models import Reminder as ReminderModel
from ...infrastructure.db.session import get_db

router = APIRouter(tags=["reminders"])

DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"


class ReminderResponse(BaseModel):
    id: str
    title: str
    timezone: str
    recurrence_frequency: str
    recurrence_interval: int
    priority: str
    channel: str
    status: str
    next_due_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None


class ReminderListResponse(BaseModel):
    items: list[ReminderResponse]
    total: int
    upcoming: int
    overdue: int
    completed: int


class SnoozeRequest(BaseModel):
    hours: float = Field(default=1.0, ge=0.1, le=168.0)


def _serialize(rem: ReminderModel) -> ReminderResponse:
    return ReminderResponse(
        id=rem.id,
        title=rem.title,
        timezone=rem.timezone,
        recurrence_frequency=rem.recurrence_frequency,
        recurrence_interval=rem.recurrence_interval,
        priority=rem.priority,
        channel=rem.channel,
        status=rem.status,
        next_due_at=rem.next_due_at,
        created_at=rem.created_at,
        updated_at=rem.updated_at,
        completed_at=rem.completed_at,
        cancelled_at=rem.cancelled_at,
    )


@router.get("/reminders", response_model=ReminderListResponse)
async def list_reminders(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ReminderListResponse:
    """List reminders with counts by status."""
    now = datetime.now(timezone.utc)
    now_naive = now.replace(tzinfo=None)

    stmt = select(ReminderModel).where(ReminderModel.workspace_id == DEFAULT_WORKSPACE_ID)
    if status_filter:
        stmt = stmt.where(ReminderModel.status == status_filter)
    stmt = stmt.order_by(ReminderModel.next_due_at.asc()).limit(limit)
    result = await db.execute(stmt)
    reminders = result.scalars().all()

    # Count by status
    active = [r for r in reminders if r.status == ReminderStatus.ACTIVE.value]
    upcoming = [r for r in active if r.next_due_at and r.next_due_at > now_naive]
    overdue = [r for r in active if r.next_due_at and r.next_due_at <= now_naive]
    completed = [r for r in reminders if r.status == ReminderStatus.COMPLETED.value]

    return ReminderListResponse(
        items=[_serialize(r) for r in reminders],
        total=len(reminders),
        upcoming=len(upcoming),
        overdue=len(overdue),
        completed=len(completed),
    )


@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ReminderResponse:
    rem = await db.get(ReminderModel, reminder_id)
    if rem is None or rem.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return _serialize(rem)


@router.post("/reminders/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(
    reminder_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ReminderResponse:
    rem = await db.get(ReminderModel, reminder_id)
    if rem is None or rem.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    if rem.status not in (ReminderStatus.ACTIVE.value, ReminderStatus.PAUSED.value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot complete reminder in status {rem.status}")
    rem.status = ReminderStatus.COMPLETED.value
    rem.completed_at = datetime.now(timezone.utc)
    rem.updated_at = datetime.now(timezone.utc)
    rem.version += 1
    await db.flush()
    return _serialize(rem)


@router.post("/reminders/{reminder_id}/snooze", response_model=ReminderResponse)
async def snooze_reminder(
    reminder_id: str,
    req: SnoozeRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ReminderResponse:
    rem = await db.get(ReminderModel, reminder_id)
    if rem is None or rem.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    if rem.status != ReminderStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot snooze reminder in status {rem.status}")
    rem.next_due_at = datetime.now(timezone.utc) + timedelta(hours=req.hours)
    rem.updated_at = datetime.now(timezone.utc)
    rem.version += 1
    await db.flush()
    return _serialize(rem)


@router.post("/reminders/{reminder_id}/cancel", response_model=ReminderResponse)
async def cancel_reminder(
    reminder_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ReminderResponse:
    rem = await db.get(ReminderModel, reminder_id)
    if rem is None or rem.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    if rem.status in (ReminderStatus.COMPLETED.value, ReminderStatus.CANCELLED.value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel reminder in status {rem.status}")
    rem.status = ReminderStatus.CANCELLED.value
    rem.cancelled_at = datetime.now(timezone.utc)
    rem.updated_at = datetime.now(timezone.utc)
    rem.version += 1
    await db.flush()
    return _serialize(rem)
