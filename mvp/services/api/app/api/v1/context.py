"""VNBOT API — Context endpoints (Hermes ADR-0011 Fase 0.8).

GET  /api/v1/context              — returns USER.md + MEMORY.md content
POST /api/v1/context/materialize  — regenerate USER.md + MEMORY.md from DB
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_workspace_id
from ...infrastructure.db.models import User, Workspace
from ...infrastructure.db.session import get_db
from ...infrastructure.llm import (
    ensure_persistence_files,
    materialize_memory_md,
    materialize_user_md,
    read_memory_md,
    read_user_md,
)

router = APIRouter(tags=["context"])

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


class ContextResponse(BaseModel):
    user_md: str
    memory_md: str
    user_md_bytes: int
    memory_md_bytes: int
    memory_cap_bytes: int


class MaterializeResponse(BaseModel):
    user_md: str
    memory_md: str
    user_md_bytes: int
    memory_md_bytes: int


@router.get("/context", response_model=ContextResponse)
async def get_context(
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ContextResponse:
    """Return the current USER.md + MEMORY.md content.

    These are the persistence files that Hermes uses for long-term context.
    The frontend uses this endpoint to display what Hermes knows about the user.
    """
    from ...infrastructure.llm import MEMORY_MD_CAP_BYTES

    ws_id = await _ensure_default_workspace(db, workspace_id)
    ensure_persistence_files(ws_id)
    user_md = await read_user_md(ws_id)
    memory_md = await read_memory_md(ws_id)
    return ContextResponse(
        user_md=user_md,
        memory_md=memory_md,
        user_md_bytes=len(user_md.encode("utf-8")),
        memory_md_bytes=len(memory_md.encode("utf-8")),
        memory_cap_bytes=MEMORY_MD_CAP_BYTES,
    )


@router.post("/context/materialize", response_model=MaterializeResponse)
async def materialize_context(
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> MaterializeResponse:
    """Regenerate USER.md + MEMORY.md from the database.

    Call this after significant changes (new memories, preferences) to refresh
    the LLM prompt context.
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
