"""VNBOT API — Health endpoints.

/healthz — liveness probe (always returns 200 if process is up)
/readyz — readiness probe (checks DB connectivity)
/dependencies — lists external dependencies and their status
/scheduler/trigger — manually trigger scheduler ticks (dev only)
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import get_settings
from ...infrastructure.db.session import get_db
from ...infrastructure.scheduler import scheduler_service
from ...infrastructure.notifications import list_channels
from ...schemas.chat import HealthResponse  # noqa: F401 — re-using for now

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    """Liveness probe — always 200 if the process is up."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
        checks={"process": "ok"},
    )


@router.get("/readyz", response_model=HealthResponse)
async def readyz(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Readiness probe — checks DB connectivity."""
    checks: dict[str, str] = {}
    overall = "ok"

    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            checks["database"] = "ok"
        else:
            checks["database"] = "degraded"
            overall = "degraded"
    except Exception as e:
        checks["database"] = f"down: {type(e).__name__}"
        overall = "down"

    return HealthResponse(
        status=overall,  # type: ignore[arg-type]
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
        checks=checks,
    )


@router.get("/dependencies", response_model=HealthResponse)
async def dependencies() -> HealthResponse:
    """List external dependencies and their status."""
    settings = get_settings()
    checks = {
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_zai_model if settings.llm_provider == "zai" else "n/a",
        "notification_channel": settings.notification_channel_default,
        "notification_channels_registered": ",".join(list_channels()),
        "storage_backend": settings.storage_backend,
        "scheduler_timezone": settings.scheduler_timezone,
        "scheduler_started": str(scheduler_service._started),
    }
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
        checks=checks,
    )


@router.post("/scheduler/trigger")
async def trigger_scheduler() -> dict:
    """Manually trigger scheduler ticks. Dev/test only.

    Runs both ticks immediately:
    - tick_generate_occurrences: scans active reminders, generates occurrences
    - tick_deliver_pending: delivers pending occurrences past their due_at
    """
    result = await scheduler_service.trigger_now()
    return {
        "triggered": True,
        "generated_occurrences": result["generated"],
        "delivered_notifications": result["delivered"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
