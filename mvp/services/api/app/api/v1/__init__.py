"""VNBOT API — v1 API routes."""

from fastapi import APIRouter

from . import audit, chat, exports, health, memories

api_router = APIRouter()
api_router.include_router(health.router)  # /healthz, /readyz, /dependencies (no prefix)
api_router.include_router(chat.router, prefix="/api/v1")  # /api/v1/chat
api_router.include_router(memories.router, prefix="/api/v1")  # /api/v1/memories
api_router.include_router(exports.router, prefix="/api/v1")  # /api/v1/export, /api/v1/import
api_router.include_router(audit.router, prefix="/api/v1")  # /api/v1/operations, /api/v1/activity
