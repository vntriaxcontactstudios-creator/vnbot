"""VNBOT API — Memory endpoints.

POST   /memories           — create a memory node
GET    /memories           — list memories (paginated)
GET    /memories/{id}      — get a single memory
PATCH  /memories/{id}      — update a memory
DELETE /memories/{id}      — soft-delete a memory (sets status=deleted)
POST   /memories/search    — FTS5 full-text search

Per docs/03-ESQUEMA-BACKEND-VNBOT.md §33 (Backend MVP acceptance):
- Create + query memory ✓
- Soft delete (active → deleted → purged in 0.5)
- Export/import (added in paso 18)
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from vnbot_domain.entities.common import Authority, Provenance, Sensitivity
from ...dependencies import get_workspace_id
from ...infrastructure.db.models import MemoryNode, User, Workspace
from ...infrastructure.db.session import get_db
from ...schemas.memories import (
    MemoryListResponse,
    MemoryNodeCreate,
    MemoryNodeResponse,
    MemoryNodeUpdate,
    MemorySearchRequest,
    MemorySearchResponse,
    MemorySearchResult,
)

router = APIRouter(tags=["memories"])

# Default user + workspace IDs (same as chat.py — single-user local mode)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"


async def _ensure_default_workspace(db: AsyncSession) -> str:
    """Idempotent: ensure default user + workspace exist."""
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

    return DEFAULT_WORKSPACE_ID


def _serialize_memory(node: MemoryNode) -> MemoryNodeResponse:
    """Convert a MemoryNode ORM instance to a response model."""
    # For Phase 0.1, content is stored as plaintext in content_ciphertext.
    # In 0.3+, this is actually ciphertext and we decrypt here.
    content = node.content_ciphertext or ""
    # Parse tags from label if present (simple convention: #tag in label)
    # In 0.5, tags become a separate column/JSON
    tags: list[str] = []
    return MemoryNodeResponse(
        id=node.id,
        workspace_id=node.workspace_id,
        type=node.type,
        label=node.label,
        content=content,
        tags=tags,
        sensitivity=node.sensitivity,
        status=node.status,
        provenance=node.provenance,
        authority=node.authority,
        confidence=node.confidence,
        valid_from=node.valid_from,
        valid_until=node.valid_until,
        created_at=node.created_at,
        updated_at=node.updated_at,
    )


# ──────────────────────────────────────────────────────────────────────────────
# CRUD
# ──────────────────────────────────────────────────────────────────────────────


@router.post("/memories", response_model=MemoryNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    req: MemoryNodeCreate,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> MemoryNodeResponse:
    """Create a new memory node."""
    ws_id = await _ensure_default_workspace(db)

    # For Phase 0.1, store content as plaintext in content_ciphertext field.
    # In 0.3+, this gets encrypted with AES-256-GCM before storage.
    node = MemoryNode(
        id=str(uuid4()),
        workspace_id=ws_id,
        type=req.type,
        label=req.label,
        content_ciphertext=req.content,
        content_format="text",
        source_type=req.source_type,
        provenance=Provenance.EXPLICIT_USER_INPUT.value,
        authority=Authority.EXPLICIT.value,
        confidence=1.0,
        sensitivity=req.sensitivity,
        status="active",
        valid_until=req.valid_until,
    )
    db.add(node)
    await db.flush()

    return _serialize_memory(node)


@router.get("/memories", response_model=MemoryListResponse)
async def list_memories(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    type_filter: str | None = Query(default=None, alias="type"),
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> MemoryListResponse:
    """List memories (paginated, most recent first)."""
    await _ensure_default_workspace(db)

    stmt = select(MemoryNode).where(
        MemoryNode.workspace_id == DEFAULT_WORKSPACE_ID,
        MemoryNode.status == "active",
    )
    if type_filter:
        stmt = stmt.where(MemoryNode.type == type_filter)

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    stmt = stmt.order_by(MemoryNode.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    nodes = result.scalars().all()

    return MemoryListResponse(
        items=[_serialize_memory(n) for n in nodes],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/memories/{memory_id}", response_model=MemoryNodeResponse)
async def get_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> MemoryNodeResponse:
    """Get a single memory by ID."""
    await _ensure_default_workspace(db)
    node = await db.get(MemoryNode, memory_id)
    if node is None or node.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id} not found",
        )
    return _serialize_memory(node)


@router.patch("/memories/{memory_id}", response_model=MemoryNodeResponse)
async def update_memory(
    memory_id: str,
    req: MemoryNodeUpdate,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> MemoryNodeResponse:
    """Update a memory node (label, content, tags, sensitivity)."""
    await _ensure_default_workspace(db)
    node = await db.get(MemoryNode, memory_id)
    if node is None or node.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id} not found",
        )

    if req.label is not None:
        node.label = req.label
    if req.content is not None:
        node.content_ciphertext = req.content
    if req.sensitivity is not None:
        node.sensitivity = req.sensitivity
    node.updated_at = datetime.now(timezone.utc)
    node.version += 1
    await db.flush()

    return _serialize_memory(node)


@router.delete("/memories/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> None:
    """Soft-delete a memory node (sets status=deleted, deleted_at=now).

    Physical purge happens in 0.5 (per docs/07 §20.3).
    """
    await _ensure_default_workspace(db)
    node = await db.get(MemoryNode, memory_id)
    if node is None or node.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id} not found",
        )

    node.status = "deleted"
    node.deleted_at = datetime.now(timezone.utc)
    node.updated_at = datetime.now(timezone.utc)
    node.version += 1
    await db.flush()


# ──────────────────────────────────────────────────────────────────────────────
# Search (FTS5)
# ──────────────────────────────────────────────────────────────────────────────


@router.post("/memories/search", response_model=MemorySearchResponse)
async def search_memories(
    req: MemorySearchRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> MemorySearchResponse:
    """Full-text search on memories using FTS5.

    Returns ranked results with snippets highlighting the matches.
    Per docs/03 §40: P95 < 100ms for 10k memories.
    """
    await _ensure_default_workspace(db)

    # Build FTS5 query — escape special characters and use prefix matching
    # FTS5 query syntax: tokens are AND-ed by default.
    # For user input, we wrap each token in quotes to avoid syntax errors.
    tokens = req.query.strip().split()
    if not tokens:
        return MemorySearchResponse(items=[], total=0, query=req.query, limit=req.limit, offset=req.offset)

    # Use MATCH with quoted tokens for safe user input
    fts_query = " ".join(f'"{t}"*' for t in tokens)  # * = prefix match

    # Two-step query: first get matching rowids + ranks, then fetch memory data.
    # FTS5 snippet/highlight functions don't play well with JOINs in SQLite,
    # so we compute the snippet in a separate query.
    fts_sql = text("""
        SELECT
            rowid,
            rank AS fts_rank,
            snippet(memory_nodes_fts, 1, '<mark>', '</mark>', '...', 20) AS content_snippet
        FROM memory_nodes_fts
        WHERE memory_nodes_fts MATCH :query
          AND memory_nodes_fts.workspace_id = :workspace_id
          AND memory_nodes_fts.status = 'active'
        ORDER BY rank
        LIMIT :limit
        OFFSET :offset
    """)

    count_sql = text("""
        SELECT COUNT(*)
        FROM memory_nodes_fts
        WHERE memory_nodes_fts MATCH :query
          AND memory_nodes_fts.workspace_id = :workspace_id
          AND memory_nodes_fts.status = 'active'
    """)

    # Step 1: FTS query
    fts_result = await db.execute(
        fts_sql,
        {
            "query": fts_query,
            "workspace_id": DEFAULT_WORKSPACE_ID,
            "limit": req.limit,
            "offset": req.offset,
        },
    )
    fts_rows = fts_result.fetchall()

    if not fts_rows:
        return MemorySearchResponse(
            items=[], total=0, query=req.query, limit=req.limit, offset=req.offset
        )

    # Step 2: fetch memory_nodes by rowid using raw SQL (rowid is implicit in SQLite)
    rowids = [row[0] for row in fts_rows]
    nodes_sql = text("""
        SELECT rowid, id, label, type, sensitivity, created_at
        FROM memory_nodes
        WHERE rowid IN :rowids
    """)
    # SQLite doesn't support IN with a list directly in text() — use a dynamic placeholder
    placeholders = ",".join(f":r{i}" for i in range(len(rowids)))
    nodes_sql = text(f"""
        SELECT rowid, id, label, type, sensitivity, created_at
        FROM memory_nodes
        WHERE rowid IN ({placeholders})
    """)
    params = {f"r{i}": rid for i, rid in enumerate(rowids)}
    nodes_result = await db.execute(nodes_sql, params)
    nodes_by_rowid = {row[0]: row for row in nodes_result.fetchall()}

    # Combine results preserving FTS rank order
    items = []
    for fts_row in fts_rows:
        rowid, fts_rank, content_snippet = fts_row[0], fts_row[1], fts_row[2]
        node = nodes_by_rowid.get(rowid)
        if node is None:
            continue
        items.append(
            MemorySearchResult(
                id=node[1],  # id
                label=node[2],  # label
                content_snippet=content_snippet or "",
                type=node[3],  # type
                sensitivity=node[4],  # sensitivity
                rank=float(fts_rank),
                created_at=node[5],  # created_at
            )
        )

    # Get total count
    total_result = await db.execute(
        count_sql,
        {"query": fts_query, "workspace_id": DEFAULT_WORKSPACE_ID},
    )
    total = total_result.scalar_one()

    return MemorySearchResponse(
        items=items,
        total=total,
        query=req.query,
        limit=req.limit,
        offset=req.offset,
    )
