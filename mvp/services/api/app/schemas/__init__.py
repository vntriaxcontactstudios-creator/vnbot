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

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ConfirmRequest",
    "ConfirmResponse",
    "ErrorResponse",
    "HealthResponse",
    "ProposalMemory",
    "ProposalReminder",
]
