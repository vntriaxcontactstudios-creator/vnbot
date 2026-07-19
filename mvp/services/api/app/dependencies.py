"""VNBOT API — Dependencies.

FastAPI dependency providers for auth, workspace isolation, rate limiting.
"""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from .config import get_settings


async def get_workspace_id(
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-Id"),
) -> str:
    """Extract workspace_id from request header.

    In Phase 0.1 (single-user local mode), this defaults to a single workspace.
    Multi-workspace support comes in 0.3.
    """
    if x_workspace_id:
        return x_workspace_id
    # Default to "default" workspace for local mode
    return "default"


async def require_auth(
    x_session: str | None = Header(default=None, alias="X-Session-Id"),
) -> str:
    """Require a valid session.

    In Phase 0.1, this is a no-op (local mode, no auth required).
    Real auth (Argon2id + HttpOnly cookies) added in 0.3.
    """
    settings = get_settings()
    if settings.is_dev:
        # Local dev mode: no auth required
        return "local-user"
    # Production: require session
    if not x_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session required",
        )
    return x_session
