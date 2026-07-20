"""VNBOT API — Lists endpoints.

GET    /api/v1/lists           — list all lists
POST   /api/v1/lists           — create a list
GET    /api/v1/lists/{id}      — get list with items
PATCH  /api/v1/lists/{id}      — update list name
DELETE /api/v1/lists/{id}      — delete list (soft)
POST   /api/v1/lists/{id}/items — add item to list
DELETE /api/v1/lists/{id}/items/{item_id} — remove item from list
POST   /api/v1/lists/{id}/items/{item_id}/complete — mark item as complete
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_workspace_id
from ...infrastructure.db.models import List, ListItem
from ...infrastructure.db.session import get_db

router = APIRouter(tags=["lists"])

DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"


class ListItemResponse(BaseModel):
    id: str
    title: str
    position: int
    status: str
    priority: str
    due_at: datetime | None = None
    created_at: datetime


class ListResponse(BaseModel):
    id: str
    name: str
    description: str | None
    status: str
    created_at: datetime
    items: list[ListItemResponse] = []


class ListSummaryResponse(BaseModel):
    id: str
    name: str
    status: str
    item_count: int
    pending_count: int
    completed_count: int
    created_at: datetime


class ListListResponse(BaseModel):
    items: list[ListSummaryResponse]
    total: int


class CreateListRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class AddItemRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    priority: str = Field(default="normal")
    due_at: datetime | None = None


@router.get("/lists", response_model=ListListResponse)
async def list_lists(
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ListListResponse:
    stmt = select(List).where(
        List.workspace_id == DEFAULT_WORKSPACE_ID,
        List.status == "active",
    ).order_by(List.created_at.desc())
    lists = (await db.execute(stmt)).scalars().all()

    summaries = []
    for lst in lists:
        items_stmt = select(ListItem).where(ListItem.list_id == lst.id)
        items = (await db.execute(items_stmt)).scalars().all()
        pending = sum(1 for i in items if i.status == "pending")
        completed = sum(1 for i in items if i.status == "completed")
        summaries.append(ListSummaryResponse(
            id=lst.id, name=lst.name, status=lst.status,
            item_count=len(items), pending_count=pending, completed_count=completed,
            created_at=lst.created_at,
        ))

    return ListListResponse(items=summaries, total=len(summaries))


@router.post("/lists", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    req: CreateListRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ListResponse:
    lst = List(
        id=str(uuid4()),
        workspace_id=DEFAULT_WORKSPACE_ID,
        name=req.name,
        description_ciphertext=req.description,
        status="active",
    )
    db.add(lst)
    await db.flush()
    return ListResponse(id=lst.id, name=lst.name, description=req.description, status=lst.status, created_at=lst.created_at, items=[])


@router.get("/lists/{list_id}", response_model=ListResponse)
async def get_list(
    list_id: str,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ListResponse:
    lst = await db.get(List, list_id)
    if lst is None or lst.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    items_stmt = select(ListItem).where(ListItem.list_id == list_id).order_by(ListItem.position)
    items = (await db.execute(items_stmt)).scalars().all()
    return ListResponse(
        id=lst.id, name=lst.name, description=lst.description_ciphertext,
        status=lst.status, created_at=lst.created_at,
        items=[ListItemResponse(id=i.id, title=i.title_ciphertext or "", position=i.position,
                                status=i.status, priority=i.priority, due_at=i.due_at, created_at=i.created_at) for i in items],
    )


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(list_id: str, db: AsyncSession = Depends(get_db), workspace_id: str = Depends(get_workspace_id)) -> None:
    lst = await db.get(List, list_id)
    if lst is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    lst.status = "deleted"
    lst.updated_at = datetime.now(timezone.utc)
    await db.flush()


@router.post("/lists/{list_id}/items", response_model=ListItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    list_id: str,
    req: AddItemRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ListItemResponse:
    lst = await db.get(List, list_id)
    if lst is None or lst.workspace_id != DEFAULT_WORKSPACE_ID:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    # Get next position
    count_stmt = select(ListItem).where(ListItem.list_id == list_id)
    existing = (await db.execute(count_stmt)).scalars().all()
    position = len(existing)
    item = ListItem(
        id=str(uuid4()),
        list_id=list_id,
        title_ciphertext=req.title,
        position=position,
        status="pending",
        priority=req.priority,
        due_at=req.due_at,
    )
    db.add(item)
    await db.flush()
    return ListItemResponse(id=item.id, title=req.title, position=position, status="pending", priority=req.priority, due_at=req.due_at, created_at=item.created_at)


@router.delete("/lists/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(list_id: str, item_id: str, db: AsyncSession = Depends(get_db), workspace_id: str = Depends(get_workspace_id)) -> None:
    item = await db.get(ListItem, item_id)
    if item is None or item.list_id != list_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item.status = "cancelled"
    item.updated_at = datetime.now(timezone.utc)
    await db.flush()


@router.post("/lists/{list_id}/items/{item_id}/complete", response_model=ListItemResponse)
async def complete_item(list_id: str, item_id: str, db: AsyncSession = Depends(get_db), workspace_id: str = Depends(get_workspace_id)) -> ListItemResponse:
    item = await db.get(ListItem, item_id)
    if item is None or item.list_id != list_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item.status = "completed"
    item.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return ListItemResponse(id=item.id, title=item.title_ciphertext or "", position=item.position, status="completed", priority=item.priority, due_at=item.due_at, created_at=item.created_at)
