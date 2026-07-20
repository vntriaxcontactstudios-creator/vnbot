"""VNBOT API — Memory Graph endpoints.

GET    /api/v1/graph/nodes           — list nodes for graph visualization
GET    /api/v1/graph/edges           — list edges (relations between memories)
POST   /api/v1/graph/edges           — create a new edge (relation between two memories)
DELETE /api/v1/graph/edges/{id}       — delete an edge
GET    /api/v1/graph/subgraph         — get subgraph from a node (depth-limited)

Per docs/03 §40:
- Default max depth: 3
- Top-K max: 50 (default 20)
- Max nodes per query: 100
- Per-query timeout: 5 seconds
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_workspace_id
from ...infrastructure.db.models import MemoryEdge, MemoryNode
from ...infrastructure.db.session import get_db

router = APIRouter(tags=["graph"])

DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"

# Relation types per docs/07 §10
RELATION_TYPES = {
    "KNOWS", "WORKS_ON", "RELATED_TO", "DEPENDS_ON",
    "REMINDER_FOR", "HAPPENS_AT", "PREFERS", "SUPERSEDES",
    "CONTRADICTS", "DERIVED_FROM", "ASSIGNED_TO", "MENTIONED_IN",
    "LOCATED_AT",
}


class GraphNode(BaseModel):
    id: str
    type: str
    label: str
    sensitivity: str
    status: str
    created_at: datetime


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: str
    confidence: float
    created_at: datetime


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    total_nodes: int
    total_edges: int


class CreateEdgeRequest(BaseModel):
    source_node_id: str = Field(..., description="ID of the source memory node")
    target_node_id: str = Field(..., description="ID of the target memory node")
    relation_type: str = Field(..., description=f"One of: {', '.join(sorted(RELATION_TYPES))}")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class CreateEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    relation: str
    confidence: float
    created_at: datetime


@router.get("/graph", response_model=GraphResponse)
async def get_graph(
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> GraphResponse:
    """Get the full memory graph (nodes + edges) for visualization."""
    # Fetch nodes
    nodes_stmt = select(MemoryNode).where(
        MemoryNode.workspace_id == DEFAULT_WORKSPACE_ID,
        MemoryNode.status == "active",
    ).order_by(MemoryNode.created_at.desc()).limit(limit)
    nodes_result = await db.execute(nodes_stmt)
    nodes = nodes_result.scalars().all()

    if not nodes:
        return GraphResponse(nodes=[], edges=[], total_nodes=0, total_edges=0)

    node_ids = [n.id for n in nodes]

    # Fetch edges between these nodes
    edges_stmt = select(MemoryEdge).where(
        MemoryEdge.workspace_id == DEFAULT_WORKSPACE_ID,
        MemoryEdge.status == "active",
        MemoryEdge.source_node_id.in_(node_ids),
        MemoryEdge.target_node_id.in_(node_ids),
    )
    edges_result = await db.execute(edges_stmt)
    edges = edges_result.scalars().all()

    return GraphResponse(
        nodes=[
            GraphNode(
                id=n.id,
                type=n.type,
                label=n.label,
                sensitivity=n.sensitivity,
                status=n.status,
                created_at=n.created_at,
            )
            for n in nodes
        ],
        edges=[
            GraphEdge(
                id=e.id,
                source=e.source_node_id,
                target=e.target_node_id,
                relation=e.relation_type,
                confidence=e.confidence,
                created_at=e.created_at,
            )
            for e in edges
        ],
        total_nodes=len(nodes),
        total_edges=len(edges),
    )


@router.get("/graph/subgraph", response_model=GraphResponse)
async def get_subgraph(
    node_id: str = Query(..., description="Starting node ID"),
    depth: int = Query(default=2, ge=1, le=3),
    max_nodes: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> GraphResponse:
    """Get a subgraph starting from a node, up to N depth levels."""
    # BFS traversal
    visited: set[str] = set()
    current_level: list[str] = [node_id]
    all_node_ids: set[str] = set()

    for _ in range(depth):
        if not current_level or len(all_node_ids) >= max_nodes:
            break

        # Fetch nodes at current level
        nodes_stmt = select(MemoryNode).where(
            MemoryNode.id.in_(current_level),
            MemoryNode.status == "active",
        )
        nodes_result = await db.execute(nodes_stmt)
        level_nodes = nodes_result.scalars().all()

        for n in level_nodes:
            all_node_ids.add(n.id)
            visited.add(n.id)

        # Fetch edges from current level
        edges_stmt = select(MemoryEdge).where(
            MemoryEdge.workspace_id == DEFAULT_WORKSPACE_ID,
            MemoryEdge.status == "active",
            MemoryEdge.source_node_id.in_(current_level),
        )
        edges_result = await db.execute(edges_stmt)
        level_edges = edges_result.scalars().all()

        # Also fetch reverse edges
        rev_edges_stmt = select(MemoryEdge).where(
            MemoryEdge.workspace_id == DEFAULT_WORKSPACE_ID,
            MemoryEdge.status == "active",
            MemoryEdge.target_node_id.in_(current_level),
        )
        rev_result = await db.execute(rev_edges_stmt)
        rev_edges = rev_result.scalars().all()

        all_edges = list(level_edges) + list(rev_edges)

        # Collect next level node IDs
        next_level: set[str] = set()
        for e in all_edges:
            if e.source_node_id not in visited:
                next_level.add(e.source_node_id)
            if e.target_node_id not in visited:
                next_level.add(e.target_node_id)

        current_level = list(next_level)[:max_nodes - len(all_node_ids)]

    # Fetch all nodes
    final_nodes_stmt = select(MemoryNode).where(
        MemoryNode.id.in_(list(all_node_ids)),
        MemoryNode.status == "active",
    )
    final_nodes = (await db.execute(final_nodes_stmt)).scalars().all()

    # Fetch all edges between these nodes
    final_edges_stmt = select(MemoryEdge).where(
        MemoryEdge.workspace_id == DEFAULT_WORKSPACE_ID,
        MemoryEdge.status == "active",
        MemoryEdge.source_node_id.in_(list(all_node_ids)),
        MemoryEdge.target_node_id.in_(list(all_node_ids)),
    )
    final_edges = (await db.execute(final_edges_stmt)).scalars().all()

    return GraphResponse(
        nodes=[
            GraphNode(id=n.id, type=n.type, label=n.label, sensitivity=n.sensitivity, status=n.status, created_at=n.created_at)
            for n in final_nodes
        ],
        edges=[
            GraphEdge(id=e.id, source=e.source_node_id, target=e.target_node_id, relation=e.relation_type, confidence=e.confidence, created_at=e.created_at)
            for e in final_edges
        ],
        total_nodes=len(final_nodes),
        total_edges=len(final_edges),
    )


@router.post("/graph/edges", response_model=CreateEdgeResponse, status_code=status.HTTP_201_CREATED)
async def create_edge(
    req: CreateEdgeRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> CreateEdgeResponse:
    """Create a relation between two memory nodes."""
    # Validate relation type
    if req.relation_type not in RELATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid relation type. Must be one of: {', '.join(sorted(RELATION_TYPES))}",
        )

    # Verify both nodes exist
    source = await db.get(MemoryNode, req.source_node_id)
    target = await db.get(MemoryNode, req.target_node_id)
    if source is None or target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source or target node not found",
        )

    edge = MemoryEdge(
        id=str(uuid4()),
        workspace_id=DEFAULT_WORKSPACE_ID,
        source_node_id=req.source_node_id,
        target_node_id=req.target_node_id,
        relation_type=req.relation_type,
        confidence=req.confidence,
        status="active",
        provenance="explicit_user_input",
        authority="explicit",
    )
    db.add(edge)
    await db.flush()

    return CreateEdgeResponse(
        id=edge.id,
        source=edge.source_node_id,
        target=edge.target_node_id,
        relation=edge.relation_type,
        confidence=edge.confidence,
        created_at=edge.created_at,
    )


@router.delete("/graph/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edge(
    edge_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> None:
    """Delete a relation (soft delete)."""
    edge = await db.get(MemoryEdge, edge_id)
    if edge is None or edge.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edge not found")
    edge.status = "deleted"
    edge.deleted_at = datetime.now(timezone.utc)
    edge.updated_at = datetime.now(timezone.utc)
    edge.version += 1
    await db.flush()
