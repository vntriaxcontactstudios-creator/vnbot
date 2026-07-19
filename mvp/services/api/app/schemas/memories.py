"""VNBOT API — Memory schemas (Pydantic v2)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MemoryNodeCreate(BaseModel):
    """POST /memories — create a new memory node."""

    label: str = Field(..., min_length=1, max_length=255, description="Short title/label")
    content: str = Field(default="", max_length=100_000, description="Full content (plaintext for now)")
    type: str = Field(default="note", description="Memory type: note, task, preference, etc.")
    tags: list[str] = Field(default_factory=list, max_length=20)
    sensitivity: Literal["public", "personal", "sensitive", "secret"] = "personal"
    source_type: str = Field(default="explicit_user_input")
    valid_until: datetime | None = None


class MemoryNodeUpdate(BaseModel):
    """PATCH /memories/{id} — update an existing memory node."""

    label: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, max_length=100_000)
    tags: list[str] | None = Field(default=None, max_length=20)
    sensitivity: Literal["public", "personal", "sensitive", "secret"] | None = None


class MemoryNodeResponse(BaseModel):
    """Memory node as returned by the API."""

    id: str
    workspace_id: str
    type: str
    label: str
    content: str  # decrypted plaintext for now (Phase 0.1 — encryption added in 0.3)
    tags: list[str] = Field(default_factory=list)
    sensitivity: str
    status: str
    provenance: str
    authority: str
    confidence: float
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    created_at: datetime
    updated_at: datetime


class MemoryListResponse(BaseModel):
    """Paginated list of memories."""

    items: list[MemoryNodeResponse]
    total: int
    limit: int
    offset: int


class MemorySearchRequest(BaseModel):
    """POST /memories/search — full-text search."""

    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sensitivity_filter: list[str] | None = None  # filter by sensitivity levels


class MemorySearchResult(BaseModel):
    """Single search result with relevance score."""

    id: str
    label: str
    content_snippet: str  # FTS5 snippet with highlighted matches
    type: str
    sensitivity: str
    rank: float  # FTS5 rank (lower = better match)
    created_at: datetime


class MemorySearchResponse(BaseModel):
    """Search response with results + metadata."""

    items: list[MemorySearchResult]
    total: int
    query: str
    limit: int
    offset: int
