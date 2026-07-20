"""VNBOT API — v1 API routes."""

from fastapi import APIRouter

from . import (
    audit,
    briefing,
    chat,
    context,
    exports,
    files,
    graph,
    health,
    learning,
    lists,
    memories,
    reminders,
    skills,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(chat.router, prefix="/api/v1")
api_router.include_router(memories.router, prefix="/api/v1")
api_router.include_router(reminders.router, prefix="/api/v1")
api_router.include_router(graph.router, prefix="/api/v1")
api_router.include_router(lists.router, prefix="/api/v1")
api_router.include_router(briefing.router, prefix="/api/v1")
api_router.include_router(files.router, prefix="/api/v1")
api_router.include_router(exports.router, prefix="/api/v1")
api_router.include_router(audit.router, prefix="/api/v1")
api_router.include_router(skills.router, prefix="/api/v1")
api_router.include_router(learning.router, prefix="/api/v1")
api_router.include_router(context.router, prefix="/api/v1")

