"""VNBOT API — Daily briefing endpoint.

GET /api/v1/briefing — generates a daily summary using LLM or heuristics.

Per docs/09 §13.4: briefing.daily is one of the 6 initial skills for Phase 0.7.
This is a preliminary implementation (Phase 0.1) that uses heuristics only.
In Phase 0.7, this will use the LLM Router + skill system.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_workspace_id
from ...infrastructure.db.models import MemoryNode, Reminder
from ...infrastructure.db.session import get_db

router = APIRouter(tags=["briefing"])

DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"


class BriefingResponse(BaseModel):
    date: str
    greeting: str
    pending_reminders: int
    overdue_reminders: int
    upcoming_reminders: list[dict]
    recent_memories: list[dict]
    summary: str
    generated_at: datetime


@router.get("/briefing", response_model=BriefingResponse)
async def get_daily_briefing(
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> BriefingResponse:
    """Generate a daily briefing using heuristics (LLM version in Phase 0.7).

    Shows:
    - Pending/overdue reminders
    - Next 3 upcoming reminders
    - Memories created in the last 24h
    - A heuristic summary
    """
    now = datetime.now(timezone.utc)
    now_naive = now.replace(tzinfo=None)
    today_str = now.strftime("%Y-%m-%d")

    # Reminders
    rem_stmt = select(Reminder).where(
        Reminder.workspace_id == DEFAULT_WORKSPACE_ID,
        Reminder.status == "active",
    ).order_by(Reminder.next_due_at.asc())
    reminders = (await db.execute(rem_stmt)).scalars().all()

    pending = [r for r in reminders if r.next_due_at and r.next_due_at > now_naive]
    overdue = [r for r in reminders if r.next_due_at and r.next_due_at <= now_naive]
    upcoming = pending[:3]

    # Recent memories (last 24h)
    yesterday = now_naive - timedelta(hours=24)
    mem_stmt = select(MemoryNode).where(
        MemoryNode.workspace_id == DEFAULT_WORKSPACE_ID,
        MemoryNode.status == "active",
        MemoryNode.created_at >= yesterday,
    ).order_by(MemoryNode.created_at.desc()).limit(5)
    recent_mems = (await db.execute(mem_stmt)).scalars().all()

    # Heuristic summary
    parts = []
    if overdue:
        parts.append(f"Tienes {len(overdue)} recordatorio(s) vencido(s).")
    if upcoming:
        next_rem = upcoming[0]
        parts.append(f"Tu próximo recordatorio es '{next_rem.title}'.")
    if recent_mems:
        parts.append(f"Ayer guardaste {len(recent_mems)} memoria(s).")
    if not parts:
        parts.append("Todo al día. Sin recordatorios pendientes.")

    hour = now.hour
    if hour < 12:
        greeting = "Buenos días"
    elif hour < 19:
        greeting = "Buenas tardes"
    else:
        greeting = "Buenas noches"

    return BriefingResponse(
        date=today_str,
        greeting=greeting,
        pending_reminders=len(pending),
        overdue_reminders=len(overdue),
        upcoming_reminders=[
            {"id": r.id, "title": r.title, "due_at": str(r.next_due_at) if r.next_due_at else None}
            for r in upcoming
        ],
        recent_memories=[
            {"id": m.id, "label": m.label, "type": m.type}
            for m in recent_mems
        ],
        summary=" ".join(parts),
        generated_at=now,
    )
