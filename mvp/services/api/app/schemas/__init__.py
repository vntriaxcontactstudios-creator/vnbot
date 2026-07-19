"""VNBOT API — Schemas package."""

from .chat import (
    ChatRequest,
    ChatResponse,
    ConfirmRequest,
    ConfirmResponse,
    ErrorResponse,
    HealthResponse,
    ProposalMemory,
    ProposalReminder,
)
from .memories import (
    MemoryListResponse,
    MemoryNodeCreate,
    MemoryNodeResponse,
    MemoryNodeUpdate,
    MemorySearchRequest,
    MemorySearchResponse,
    MemorySearchResult,
)

__all__ = [
    # Chat
    "ChatRequest",
    "ChatResponse",
    "ConfirmRequest",
    "ConfirmResponse",
    "ErrorResponse",
    "HealthResponse",
    "ProposalMemory",
    "ProposalReminder",
    # Memories
    "MemoryListResponse",
    "MemoryNodeCreate",
    "MemoryNodeResponse",
    "MemoryNodeUpdate",
    "MemorySearchRequest",
    "MemorySearchResponse",
    "MemorySearchResult",
]
