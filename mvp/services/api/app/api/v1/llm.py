"""VNBOT API — LLM providers endpoints (ADR-0012).

GET  /api/v1/llm/providers  — list all configured providers + status
POST /api/v1/llm/test       — test a specific provider with a sample prompt
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_workspace_id
from ...infrastructure.db.session import get_db
from ...infrastructure.llm import (
    call_provider,
    get_enabled_providers,
    get_provider_configs,
    list_available_providers,
    ProviderConfig,
)

router = APIRouter(tags=["llm"])


class ProviderInfo(BaseModel):
    name: str
    model: str
    base_url: str
    api_shape: str
    enabled: bool
    has_api_key: bool
    is_default: bool


class ProvidersListResponse(BaseModel):
    items: list[ProviderInfo]
    total: int
    enabled_count: int


class TestProviderRequest(BaseModel):
    provider: str = Field(..., description="Provider name: zai|openai|anthropic|gemini|ollama")
    prompt: str = Field(default="Hello, respond with just 'OK'.", max_length=500)


class TestProviderResponse(BaseModel):
    provider: str
    model: str
    success: bool
    content: str | None = None
    tokens_used: int = 0
    latency_ms: int = 0
    error: str | None = None


@router.get("/llm/providers", response_model=ProvidersListResponse)
async def list_providers(
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ProvidersListResponse:
    """List all configured LLM providers with their status."""
    providers = list_available_providers()
    enabled = [p for p in providers if p["enabled"]]
    return ProvidersListResponse(
        items=[ProviderInfo(**p) for p in providers],
        total=len(providers),
        enabled_count=len(enabled),
    )


@router.post("/llm/test", response_model=TestProviderResponse)
async def test_provider(
    req: TestProviderRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> TestProviderResponse:
    """Test a specific LLM provider with a sample prompt."""
    import time

    # Find the provider
    configs = get_provider_configs()
    provider_cfg: ProviderConfig | None = None
    for cfg in configs:
        if cfg.name == req.provider:
            provider_cfg = cfg
            break

    if provider_cfg is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{req.provider}' not found",
        )

    if not provider_cfg.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{req.provider}' is not enabled (set API key env var)",
        )

    start = time.monotonic()
    content, tokens, error = await call_provider(
        provider_cfg,
        system_prompt="You are a test assistant. Respond with just 'OK'.",
        user_message=req.prompt,
    )
    latency_ms = int((time.monotonic() - start) * 1000)

    return TestProviderResponse(
        provider=provider_cfg.name,
        model=provider_cfg.model,
        success=content is not None,
        content=content,
        tokens_used=tokens,
        latency_ms=latency_ms,
        error=error,
    )
