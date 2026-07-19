"""VNBOT API — Health endpoints.

/healthz — liveness probe (always returns 200 if process is up)
/readyz — readiness probe (checks DB connectivity)
/dependencies — lists external dependencies and their status
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import get_settings
from ...infrastructure.db.session import get_db
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
        "storage_backend": settings.storage_backend,
        "scheduler_timezone": settings.scheduler_timezone,
    }
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
        checks=checks,
    )
