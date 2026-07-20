"""VNBOT API — Multi-LLM providers (ADR-0012).

Per ADR-0012: VNBOT supports multiple cloud LLM providers with chain fallback.
Priority order (configurable via LLM_PROVIDER env var):
  1. zai (default, no API key needed — glm-4.6)
  2. openai (gpt-4o-mini, gpt-4o)
  3. anthropic (claude-3-5-haiku, claude-3-5-sonnet)
  4. gemini (gemini-1.5-flash, gemini-1.5-pro)
  5. ollama (local, llama3.2, qwen2.5)
  6. heuristic fallback (ADR-0007, no LLM)

All providers use the OpenAI-compatible /chat/completions interface where
possible (Z.AI, OpenAI, Ollama, Gemini via OpenAI-compat endpoint). Anthropic
uses its native Messages API.

The router tries providers in order until one succeeds. If all fail, the
caller (chat.py) falls back to heuristics per ADR-0007.

API keys are read from env vars:
  - LLM_ZAI_API_KEY (optional — Z.AI works without it)
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY
  - GEMINI_API_KEY
  - OLLAMA_HOST (default: http://localhost:11434)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from ...config import get_settings

logger = logging.getLogger("vnbot.api.llm.providers")


@dataclass
class ProviderConfig:
    """Configuration for a single LLM provider."""

    name: str
    base_url: str
    model: str
    api_key: str | None
    # Some providers (Anthropic) use a different API shape
    api_shape: str = "openai"  # openai | anthropic | gemini
    # Max tokens for parse responses (keep small — we want JSON only)
    max_tokens: int = 600
    temperature: float = 0.3
    timeout: float = 15.0
    # Whether this provider is enabled (has API key or is keyless)
    enabled: bool = True


def get_provider_configs() -> list[ProviderConfig]:
    """Return all configured providers in priority order.

    The first enabled provider is the primary; the rest are fallbacks.
    """
    settings = get_settings()
    import os

    providers: list[ProviderConfig] = []

    # ─── 1. Z.AI (default, keyless) ───
    providers.append(
        ProviderConfig(
            name="zai",
            base_url=settings.llm_zai_base_url,
            model=settings.llm_zai_model,
            api_key=settings.llm_api_key or os.environ.get("LLM_ZAI_API_KEY"),
            api_shape="openai",
            enabled=settings.llm_provider == "zai" or settings.llm_provider == "auto",
        )
    )

    # ─── 2. OpenAI ───
    openai_key = os.environ.get("OPENAI_API_KEY")
    providers.append(
        ProviderConfig(
            name="openai",
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=openai_key,
            api_shape="openai",
            enabled=bool(openai_key) and settings.llm_provider in ("auto", "openai"),
        )
    )

    # ─── 3. Anthropic ───
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    providers.append(
        ProviderConfig(
            name="anthropic",
            base_url=os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"),
            api_key=anthropic_key,
            api_shape="anthropic",
            enabled=bool(anthropic_key) and settings.llm_provider in ("auto", "anthropic"),
        )
    )

    # ─── 4. Gemini (via OpenAI-compat endpoint) ───
    gemini_key = os.environ.get("GEMINI_API_KEY")
    providers.append(
        ProviderConfig(
            name="gemini",
            base_url=os.environ.get(
                "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai"
            ),
            model=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
            api_key=gemini_key,
            api_shape="openai",
            enabled=bool(gemini_key) and settings.llm_provider in ("auto", "gemini"),
        )
    )

    # ─── 5. Ollama (local) ───
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    providers.append(
        ProviderConfig(
            name="ollama",
            base_url=f"{ollama_host}/v1",
            model=os.environ.get("OLLAMA_MODEL", "llama3.2"),
            api_key="ollama",  # Ollama doesn't need a real key, but field is required
            api_shape="openai",
            timeout=30.0,  # local models can be slow on first call
            enabled=settings.llm_provider in ("auto", "ollama"),
        )
    )

    return providers


def get_enabled_providers() -> list[ProviderConfig]:
    """Return only enabled providers (in priority order)."""
    return [p for p in get_provider_configs() if p.enabled]


def list_available_providers() -> list[dict]:
    """Return provider info for the /api/v1/llm/providers endpoint."""
    configs = get_provider_configs()
    return [
        {
            "name": p.name,
            "model": p.model,
            "base_url": p.base_url,
            "api_shape": p.api_shape,
            "enabled": p.enabled,
            "has_api_key": bool(p.api_key) or p.name in ("zai", "ollama"),
            "is_default": p.name == get_settings().llm_provider,
        }
        for p in configs
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Provider call implementations
# ──────────────────────────────────────────────────────────────────────────────


async def call_provider(
    provider: ProviderConfig,
    system_prompt: str,
    user_message: str,
) -> tuple[str | None, int, str | None]:
    """Call a single LLM provider. Returns (content, tokens_used, error).

    Returns (None, 0, error_message) on failure.
    Returns (content, tokens, None) on success.
    """
    try:
        if provider.api_shape == "openai":
            return await _call_openai_compatible(provider, system_prompt, user_message)
        elif provider.api_shape == "anthropic":
            return await _call_anthropic(provider, system_prompt, user_message)
        else:
            return None, 0, f"Unknown API shape: {provider.api_shape}"
    except httpx.TimeoutException:
        return None, 0, "timeout"
    except Exception as e:
        return None, 0, f"{type(e).__name__}: {e}"


async def _call_openai_compatible(
    provider: ProviderConfig,
    system_prompt: str,
    user_message: str,
) -> tuple[str | None, int, str | None]:
    """Call a provider using the OpenAI-compatible /chat/completions endpoint.

    Used by: Z.AI, OpenAI, Gemini (via compat), Ollama.
    """
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if provider.api_key:
        headers["Authorization"] = f"Bearer {provider.api_key}"

    payload = {
        "model": provider.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": provider.temperature,
        "max_tokens": provider.max_tokens,
    }

    async with httpx.AsyncClient(timeout=provider.timeout) as client:
        response = await client.post(
            f"{provider.base_url}/chat/completions",
            json=payload,
            headers=headers,
        )

        if response.status_code != 200:
            return None, 0, f"HTTP {response.status_code}: {response.text[:200]}"

        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        tokens = data.get("usage", {}).get("total_tokens", 0)
        return content, tokens, None


async def _call_anthropic(
    provider: ProviderConfig,
    system_prompt: str,
    user_message: str,
) -> tuple[str | None, int, str | None]:
    """Call Anthropic using the native Messages API."""
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "x-api-key": provider.api_key or "",
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": provider.model,
        "max_tokens": provider.max_tokens,
        "temperature": provider.temperature,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_message},
        ],
    }

    async with httpx.AsyncClient(timeout=provider.timeout) as client:
        response = await client.post(
            f"{provider.base_url}/v1/messages",
            json=payload,
            headers=headers,
        )

        if response.status_code != 200:
            return None, 0, f"HTTP {response.status_code}: {response.text[:200]}"

        data = response.json()
        # Anthropic returns content blocks
        content_blocks = data.get("content", [])
        content = "".join(
            block.get("text", "") for block in content_blocks if block.get("type") == "text"
        ).strip()
        tokens = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get(
            "output_tokens", 0
        )
        return content, tokens, None


# ──────────────────────────────────────────────────────────────────────────────
# Chain fallback — try providers in order until one succeeds
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class ChainResult:
    """Result from the chain fallback attempt."""

    content: str | None
    tokens_used: int
    provider_used: str | None
    errors: list[dict]  # [{provider, error}, ...]


async def call_with_chain_fallback(
    system_prompt: str,
    user_message: str,
    preferred_provider: str | None = None,
) -> ChainResult:
    """Try providers in priority order until one succeeds.

    Args:
        system_prompt: The system prompt (already built with USER.md + MEMORY.md context)
        user_message: The user's input message
        preferred_provider: If set, try this provider first (overrides priority)

    Returns ChainResult with content from the first successful provider,
    or content=None if all failed (caller should fall back to heuristics).
    """
    providers = get_enabled_providers()

    # If preferred_provider specified, move it to front
    if preferred_provider:
        for i, p in enumerate(providers):
            if p.name == preferred_provider:
                providers.insert(0, providers.pop(i))
                break

    if not providers:
        logger.warning("No LLM providers enabled — falling back to heuristics")
        return ChainResult(content=None, tokens_used=0, provider_used=None, errors=[])

    errors: list[dict] = []

    for provider in providers:
        logger.debug(f"[LLM chain] trying {provider.name} ({provider.model})")
        content, tokens, error = await call_provider(provider, system_prompt, user_message)

        if content is not None:
            logger.info(
                f"[LLM chain] {provider.name} succeeded ({len(content)} chars, {tokens} tokens)"
            )
            return ChainResult(
                content=content,
                tokens_used=tokens,
                provider_used=provider.name,
                errors=errors,
            )

        errors.append({"provider": provider.name, "error": error or "unknown error"})
        logger.warning(f"[LLM chain] {provider.name} failed: {error}")

    logger.warning(
        f"[LLM chain] all {len(providers)} providers failed: "
        f"{[e['provider'] for e in errors]}"
    )
    return ChainResult(content=None, tokens_used=0, provider_used=None, errors=errors)
