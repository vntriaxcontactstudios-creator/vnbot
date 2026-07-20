"""VNBOT API — Skills endpoints (Hermes ADR-0009 Fase 0.7).

GET    /api/v1/skills                — list all skills (filterable by status/origin)
POST   /api/v1/skills                — create a hand-authored skill
GET    /api/v1/skills/{id}           — get skill detail
PATCH  /api/v1/skills/{id}           — update skill body/description/triggers
DELETE /api/v1/skills/{id}           — soft-delete (status=archived)
POST   /api/v1/skills/{id}/activate  — promote draft → active
POST   /api/v1/skills/{id}/use       — increment use_count (called when skill is referenced)
POST   /api/v1/skills/materialize    — regenerate MEMORY.md + USER.md from DB
GET    /api/v1/skills/{id}/history   — view LearningLog entries for this skill
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_workspace_id
from ...infrastructure.db.models import LearningLog, Skill, User, Workspace
from ...infrastructure.db.session import get_db
from ...infrastructure.llm import (
    ensure_persistence_files,
    materialize_memory_md,
    materialize_user_md,
)

router = APIRouter(tags=["skills"])

DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


async def _ensure_default_workspace(db: AsyncSession, workspace_id: str) -> str:
    """Ensure workspace + user exist. If header provided a custom workspace_id,
    we use that (after ensuring the default workspace exists for FK integrity).
    Returns the effective workspace_id to use.
    """
    # Always ensure the default user + workspace exist (idempotent)
    user = await db.get(User, DEFAULT_USER_ID)
    if user is None:
        user = User(
            id=DEFAULT_USER_ID,
            email=None,
            display_name="Local User",
            status="active",
            timezone="America/Caracas",
            locale="es",
        )
        db.add(user)
        await db.flush()

    ws = await db.get(Workspace, DEFAULT_WORKSPACE_ID)
    if ws is None:
        ws = Workspace(
            id=DEFAULT_WORKSPACE_ID,
            owner_user_id=DEFAULT_USER_ID,
            name="Personal",
            type="personal",
            default_timezone="America/Caracas",
            settings_json={},
        )
        db.add(ws)
        await db.flush()

    # If caller passed a custom workspace_id that isn't the default, use default
    # (since other workspace IDs don't exist in single-user local mode)
    if workspace_id == "default" or workspace_id != DEFAULT_WORKSPACE_ID:
        return DEFAULT_WORKSPACE_ID
    return workspace_id


# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────


class SkillResponse(BaseModel):
    id: str
    name: str
    description: str
    body_markdown: str
    triggers_json: dict
    status: str
    origin: str
    version: int
    confidence: float
    use_count: int
    last_used_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class SkillSummaryResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    origin: str
    version: int
    confidence: float
    use_count: int
    last_used_at: datetime | None = None
    created_at: datetime


class SkillListResponse(BaseModel):
    items: list[SkillSummaryResponse]
    total: int


class CreateSkillRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)
    body_markdown: str = Field(..., min_length=1, max_length=10000)
    triggers_json: dict = Field(default_factory=dict)
    status: str = Field(default="draft", pattern="^(draft|active|deprecated|archived)$")
    tags: list[str] = Field(default_factory=list)


class PatchSkillRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    body_markdown: str | None = Field(default=None, min_length=1, max_length=10000)
    triggers_json: dict | None = None
    status: str | None = Field(default=None, pattern="^(draft|active|deprecated|archived)$")
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class MaterializeResponse(BaseModel):
    user_md: str
    memory_md: str
    memory_md_bytes: int
    user_md_bytes: int


class SkillHistoryEntry(BaseModel):
    id: str
    action: str
    trigger_reason: str | None
    outcome_summary: str
    success: bool
    created_at: datetime


class SkillHistoryResponse(BaseModel):
    items: list[SkillHistoryEntry]
    total: int


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _to_response(skill: Skill) -> SkillResponse:
    return SkillResponse(
        id=skill.id,
        name=skill.name,
        description=skill.description,
        body_markdown=skill.body_markdown,
        triggers_json=skill.triggers_json or {},
        status=skill.status,
        origin=skill.origin,
        version=skill.version,
        confidence=skill.confidence,
        use_count=skill.use_count,
        last_used_at=skill.last_used_at,
        created_at=skill.created_at,
        updated_at=skill.updated_at,
    )


def _to_summary(skill: Skill) -> SkillSummaryResponse:
    return SkillSummaryResponse(
        id=skill.id,
        name=skill.name,
        description=skill.description,
        status=skill.status,
        origin=skill.origin,
        version=skill.version,
        confidence=skill.confidence,
        use_count=skill.use_count,
        last_used_at=skill.last_used_at,
        created_at=skill.created_at,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/skills", response_model=SkillListResponse)
async def list_skills(
    status_filter: str | None = Query(default=None, alias="status"),
    origin: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> SkillListResponse:
    """List all skills, optionally filtered by status or origin."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    stmt = (
        select(Skill)
        .where(
            Skill.workspace_id == ws_id,
            Skill.deleted_at.is_(None),
        )
        .order_by(Skill.updated_at.desc())
    )
    if status_filter:
        stmt = stmt.where(Skill.status == status_filter)
    if origin:
        stmt = stmt.where(Skill.origin == origin)

    result = await db.execute(stmt)
    skills = result.scalars().all()
    ws_id = ws_id  # silence unused warning
    return SkillListResponse(
        items=[_to_summary(s) for s in skills],
        total=len(skills),
    )


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    req: CreateSkillRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> SkillResponse:
    """Create a new hand-authored skill."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    # Check for duplicate name
    existing = await db.execute(
        select(Skill).where(
            Skill.workspace_id == ws_id,
            Skill.name == req.name,
            Skill.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Skill with name '{req.name}' already exists in this workspace",
        )

    skill = Skill(
        id=str(uuid4()),
        workspace_id=ws_id,
        name=req.name,
        description=req.description,
        body_markdown=req.body_markdown,
        triggers_json=req.triggers_json,
        status=req.status,
        origin="user",
        version=1,
        confidence=0.5,
    )
    db.add(skill)
    await db.flush()  # ensure skill.id exists before referencing in log

    # Write audit log
    log_entry = LearningLog(
        id=str(uuid4()),
        workspace_id=ws_id,
        action="skill_created",
        origin="user",
        trigger_reason="manual creation via API",
        review_json={"name": req.name, "status": req.status},
        outcome_summary=f"user created skill '{req.name}' (status={req.status})",
        skill_id=skill.id,
        success=True,
    )
    db.add(log_entry)
    await db.commit()

    return _to_response(skill)


@router.get("/skills/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> SkillResponse:
    """Get a single skill by ID."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.workspace_id != ws_id or skill.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return _to_response(skill)


@router.patch("/skills/{skill_id}", response_model=SkillResponse)
async def patch_skill(
    skill_id: str,
    req: PatchSkillRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> SkillResponse:
    """Update a skill. Increments version on body/triggers changes."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.workspace_id != ws_id or skill.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    changes: list[str] = []
    if req.name is not None and req.name != skill.name:
        skill.name = req.name
        changes.append("name")
    if req.description is not None and req.description != skill.description:
        skill.description = req.description
        changes.append("description")
    if req.body_markdown is not None and req.body_markdown != skill.body_markdown:
        skill.body_markdown = req.body_markdown
        changes.append("body_markdown")
        skill.version += 1
    if req.triggers_json is not None and req.triggers_json != skill.triggers_json:
        skill.triggers_json = req.triggers_json
        changes.append("triggers_json")
        skill.version += 1
    if req.status is not None and req.status != skill.status:
        skill.status = req.status
        changes.append(f"status→{req.status}")
    if req.confidence is not None and req.confidence != skill.confidence:
        skill.confidence = req.confidence
        changes.append(f"confidence→{req.confidence:.2f}")

    if changes:
        skill.updated_at = datetime.now(timezone.utc)
        # Write audit log
        log_entry = LearningLog(
            id=str(uuid4()),
            workspace_id=ws_id,
            action="skill_patched",
            origin="user",
            trigger_reason="manual patch via API",
            review_json={"changes": changes},
            outcome_summary=f"patched skill '{skill.name}' v{skill.version}: {', '.join(changes)}",
            skill_id=skill.id,
            success=True,
        )
        db.add(log_entry)

    await db.commit()
    return _to_response(skill)


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> None:
    """Soft-delete a skill (sets status=archived, deleted_at=now)."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.workspace_id != ws_id or skill.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    skill.status = "archived"
    skill.deleted_at = datetime.now(timezone.utc)

    log_entry = LearningLog(
        id=str(uuid4()),
        workspace_id=ws_id,
        action="skill_patched",
        origin="user",
        trigger_reason="manual delete via API",
        review_json={},
        outcome_summary=f"archived skill '{skill.name}'",
        skill_id=skill.id,
        success=True,
    )
    db.add(log_entry)
    await db.commit()


@router.post("/skills/{skill_id}/activate", response_model=SkillResponse)
async def activate_skill(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> SkillResponse:
    """Promote a draft skill to active status."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.workspace_id != ws_id or skill.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    if skill.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Skill is in status '{skill.status}', can only activate from 'draft'",
        )

    skill.status = "active"
    skill.confidence = max(skill.confidence, 0.5)  # bump confidence on activation
    skill.updated_at = datetime.now(timezone.utc)

    log_entry = LearningLog(
        id=str(uuid4()),
        workspace_id=ws_id,
        action="skill_patched",
        origin="user",
        trigger_reason="manual activation via API",
        review_json={},
        outcome_summary=f"activated skill '{skill.name}' (confidence→{skill.confidence:.2f})",
        skill_id=skill.id,
        success=True,
    )
    db.add(log_entry)
    await db.commit()
    return _to_response(skill)


@router.post("/skills/{skill_id}/use", response_model=SkillResponse)
async def record_skill_use(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> SkillResponse:
    """Record a use of this skill (increments use_count, bumps confidence slightly)."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.workspace_id != ws_id or skill.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    skill.use_count += 1
    skill.last_used_at = datetime.now(timezone.utc)
    # Confidence grows with successful uses, capped at 1.0
    skill.confidence = min(1.0, skill.confidence + 0.05)
    skill.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return _to_response(skill)


@router.post("/skills/materialize", response_model=MaterializeResponse)
async def materialize_persistence_files(
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> MaterializeResponse:
    """Regenerate USER.md + MEMORY.md from the database.

    Called after significant changes (new memories, preferences updated) to
    keep the LLM prompt context fresh.
    """
    ws_id = await _ensure_default_workspace(db, workspace_id)
    ensure_persistence_files(ws_id)
    user_md = await materialize_user_md(db, ws_id)
    memory_md = await materialize_memory_md(db, ws_id)
    return MaterializeResponse(
        user_md=user_md,
        memory_md=memory_md,
        user_md_bytes=len(user_md.encode("utf-8")),
        memory_md_bytes=len(memory_md.encode("utf-8")),
    )


@router.get("/skills/{skill_id}/history", response_model=SkillHistoryResponse)
async def skill_history(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> SkillHistoryResponse:
    """View the LearningLog history for a skill (creation, patches, uses)."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.workspace_id != ws_id or skill.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    stmt = (
        select(LearningLog)
        .where(
            LearningLog.workspace_id == ws_id,
            LearningLog.skill_id == skill_id,
        )
        .order_by(LearningLog.created_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return SkillHistoryResponse(
        items=[
            SkillHistoryEntry(
                id=log.id,
                action=log.action,
                trigger_reason=log.trigger_reason,
                outcome_summary=log.outcome_summary,
                success=log.success,
                created_at=log.created_at,
            )
            for log in logs
        ],
        total=len(logs),
    )
