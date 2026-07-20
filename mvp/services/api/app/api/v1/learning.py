"""VNBOT API — Learning endpoints (Hermes ADR-0009 Fase 0.7).

GET  /api/v1/learning              — list recent learning log entries
GET  /api/v1/learning/{id}         — get a single learning log entry by ID
GET  /api/v1/learning/summary      — summary stats (counts by action, success rate)
POST /api/v1/learning/curate       — manually trigger memory curation
POST /api/v1/learning/review       — manually trigger a background review
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import Integer, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_workspace_id
from ...infrastructure.db.models import LearningLog, User, Workspace
from ...infrastructure.db.session import get_db
from ...infrastructure.llm import background_review, memory_curation

router = APIRouter(tags=["learning"])

DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


async def _ensure_default_workspace(db: AsyncSession, workspace_id: str) -> str:
    """Ensure workspace + user exist. Returns the effective workspace_id."""
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

    if workspace_id == "default" or workspace_id != DEFAULT_WORKSPACE_ID:
        return DEFAULT_WORKSPACE_ID
    return workspace_id


# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────


class LearningLogResponse(BaseModel):
    id: str
    action: str
    origin: str
    trigger_reason: str | None
    review_json: dict
    outcome_summary: str
    memory_ids: list[str]
    skill_id: str | None
    llm_model: str | None
    llm_tokens_used: int
    success: bool
    error_message: str | None
    created_at: datetime


class LearningListResponse(BaseModel):
    items: list[LearningLogResponse]
    total: int


class LearningSummaryResponse(BaseModel):
    total_entries: int
    successful: int
    failed: int
    success_rate: float
    by_action: dict[str, int]
    by_origin: dict[str, int]
    total_tokens_used: int
    last_24h_count: int
    last_7d_count: int


class ProviderUsageEntry(BaseModel):
    provider: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    total_tokens: int
    avg_tokens_per_call: float
    last_used: str | None = None


class CostTrackingResponse(BaseModel):
    providers: list[ProviderUsageEntry]
    total_tokens: int
    total_calls: int
    estimated_cost_usd: float  # rough estimate based on token prices
    period_start: str
    period_end: str


class ManualReviewRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=5000)
    assistant_response: str = Field(..., min_length=1, max_length=5000)
    intent: str = Field(default="unknown")
    used_llm: bool = Field(default=False)


class ManualReviewResponse(BaseModel):
    memories_to_save: list[dict]
    nothing_to_learn: bool
    error: str | None
    llm_tokens_used: int


class CurationResponse(BaseModel):
    started_at: str
    total_memories_before: int
    total_memories_after: int
    demoted_low_confidence: int
    compressed_old_entries: int
    kept_active: int
    bytes_estimate: int


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _to_response(log: LearningLog) -> LearningLogResponse:
    return LearningLogResponse(
        id=log.id,
        action=log.action,
        origin=log.origin,
        trigger_reason=log.trigger_reason,
        review_json=log.review_json or {},
        outcome_summary=log.outcome_summary,
        memory_ids=log.memory_ids_json or [],
        skill_id=log.skill_id,
        llm_model=log.llm_model,
        llm_tokens_used=log.llm_tokens_used,
        success=log.success,
        error_message=log.error_message,
        created_at=log.created_at,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/learning", response_model=LearningListResponse)
async def list_learning(
    action: str | None = Query(default=None),
    origin: str | None = Query(default=None),
    success: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> LearningListResponse:
    """List recent learning log entries, filterable."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    stmt = (
        select(LearningLog)
        .where(LearningLog.workspace_id == ws_id)
        .order_by(LearningLog.created_at.desc())
        .limit(limit)
    )
    if action:
        stmt = stmt.where(LearningLog.action == action)
    if origin:
        stmt = stmt.where(LearningLog.origin == origin)
    if success is not None:
        stmt = stmt.where(LearningLog.success == success)

    result = await db.execute(stmt)
    logs = result.scalars().all()
    return LearningListResponse(
        items=[_to_response(log) for log in logs],
        total=len(logs),
    )


@router.get("/learning/summary", response_model=LearningSummaryResponse)
async def learning_summary(
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> LearningSummaryResponse:
    """Return summary stats about Hermes learning activity."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    # Total counts
    total = (
        await db.execute(
            select(func.count(LearningLog.id)).where(LearningLog.workspace_id == ws_id)
        )
    ).scalar_one()

    successful = (
        await db.execute(
            select(func.count(LearningLog.id)).where(
                LearningLog.workspace_id == ws_id,
                LearningLog.success.is_(True),
            )
        )
    ).scalar_one()

    failed = total - successful
    success_rate = (successful / total) if total > 0 else 0.0

    # By action
    action_stmt = (
        select(LearningLog.action, func.count(LearningLog.id))
        .where(LearningLog.workspace_id == ws_id)
        .group_by(LearningLog.action)
    )
    action_result = await db.execute(action_stmt)
    by_action = {row[0]: row[1] for row in action_result}

    # By origin
    origin_stmt = (
        select(LearningLog.origin, func.count(LearningLog.id))
        .where(LearningLog.workspace_id == ws_id)
        .group_by(LearningLog.origin)
    )
    origin_result = await db.execute(origin_stmt)
    by_origin = {row[0]: row[1] for row in origin_result}

    # Total tokens
    total_tokens = (
        await db.execute(
            select(func.coalesce(func.sum(LearningLog.llm_tokens_used), 0)).where(
                LearningLog.workspace_id == ws_id
            )
        )
    ).scalar_one()

    # Last 24h / 7d counts
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    count_24h = (
        await db.execute(
            select(func.count(LearningLog.id)).where(
                LearningLog.workspace_id == ws_id,
                LearningLog.created_at >= last_24h,
            )
        )
    ).scalar_one()
    count_7d = (
        await db.execute(
            select(func.count(LearningLog.id)).where(
                LearningLog.workspace_id == ws_id,
                LearningLog.created_at >= last_7d,
            )
        )
    ).scalar_one()

    return LearningSummaryResponse(
        total_entries=total,
        successful=successful,
        failed=failed,
        success_rate=success_rate,
        by_action=by_action,
        by_origin=by_origin,
        total_tokens_used=total_tokens,
        last_24h_count=count_24h,
        last_7d_count=count_7d,
    )


@router.get("/learning/{log_id}", response_model=LearningLogResponse)
async def get_learning_entry(
    log_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> LearningLogResponse:
    """Get a single learning log entry by ID."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    log = await db.get(LearningLog, log_id)
    if log is None or log.workspace_id != ws_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning log not found")
    return _to_response(log)


@router.post("/learning/curate", response_model=CurationResponse)
async def trigger_curation(
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> CurationResponse:
    """Manually trigger memory curation (normally runs every 6h)."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    summary = await memory_curation(workspace_id=ws_id)
    return CurationResponse(
        started_at=summary.get("started_at", ""),
        total_memories_before=summary.get("total_memories_before", 0),
        total_memories_after=summary.get("total_memories_after", 0),
        demoted_low_confidence=summary.get("demoted_low_confidence", 0),
        compressed_old_entries=summary.get("compressed_old_entries", 0),
        kept_active=summary.get("kept_active", 0),
        bytes_estimate=summary.get("bytes_estimate", 0),
    )


@router.post("/learning/review", response_model=ManualReviewResponse)
async def trigger_review(
    req: ManualReviewRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ManualReviewResponse:
    """Manually trigger a background review (normally runs after each chat confirm)."""
    ws_id = await _ensure_default_workspace(db, workspace_id)
    result = await background_review(
        user_input=req.user_input,
        assistant_response=req.assistant_response,
        intent=req.intent,
        used_llm=req.used_llm,
        workspace_id=ws_id,
    )
    return ManualReviewResponse(
        memories_to_save=result.memories_to_save,
        nothing_to_learn=result.nothing_to_learn,
        error=result.error,
        llm_tokens_used=result.llm_tokens_used,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Cost tracking (ADR-0012)
# ──────────────────────────────────────────────────────────────────────────────


# Rough token prices (USD per 1M tokens, as of 2026-07). For estimation only.
PROVIDER_PRICE_PER_1M_TOKENS: dict[str, float] = {
    "zai": 0.0,  # free tier (keyless)
    "openai": 0.15,  # gpt-4o-mini blended
    "anthropic": 0.25,  # claude-3-5-haiku blended
    "gemini": 0.075,  # gemini-1.5-flash
    "ollama": 0.0,  # local
}


@router.get("/learning/costs", response_model=CostTrackingResponse)
async def cost_tracking(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> CostTrackingResponse:
    """Per-provider cost tracking for the last N days (default 30).

    Returns token usage broken down by provider, with a rough cost estimate.
    """
    from datetime import timedelta

    ws_id = await _ensure_default_workspace(db, workspace_id)
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=days)

    # Aggregate by provider (or 'unknown' for legacy entries)
    stmt = (
        select(
            func.coalesce(LearningLog.llm_provider, "unknown").label("provider"),
            func.count(LearningLog.id).label("total_calls"),
            func.sum(LearningLog.success.cast(Integer)).label("successful_calls"),
            func.coalesce(func.sum(LearningLog.llm_tokens_used), 0).label("total_tokens"),
            func.max(LearningLog.created_at).label("last_used"),
        )
        .where(
            LearningLog.workspace_id == ws_id,
            LearningLog.created_at >= period_start,
        )
        .group_by("provider")
        .order_by(func.coalesce(func.sum(LearningLog.llm_tokens_used), 0).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    providers: list[ProviderUsageEntry] = []
    total_tokens = 0
    total_calls = 0
    estimated_cost = 0.0

    for row in rows:
        provider_name = row.provider
        tokens = int(row.total_tokens or 0)
        calls = int(row.total_calls or 0)
        successful = int(row.successful_calls or 0)

        price = PROVIDER_PRICE_PER_1M_TOKENS.get(provider_name, 0.0)
        cost = (tokens / 1_000_000) * price

        providers.append(
            ProviderUsageEntry(
                provider=provider_name,
                total_calls=calls,
                successful_calls=successful,
                failed_calls=calls - successful,
                total_tokens=tokens,
                avg_tokens_per_call=round(tokens / calls, 1) if calls > 0 else 0.0,
                last_used=row.last_used.isoformat() if row.last_used else None,
            )
        )
        total_tokens += tokens
        total_calls += calls
        estimated_cost += cost

    return CostTrackingResponse(
        providers=providers,
        total_tokens=total_tokens,
        total_calls=total_calls,
        estimated_cost_usd=round(estimated_cost, 4),
        period_start=period_start.isoformat(),
        period_end=now.isoformat(),
    )
