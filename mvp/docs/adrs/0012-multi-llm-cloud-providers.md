# ADR-0012: Multi-LLM Cloud Provider Support with Chain Fallback

**Status:** Accepted
**Date:** 2026-07-20
**Supersedes:** —
**Superseded by:** —
**Related:** ADR-0007 (mandatory heuristic fallback), ADR-0011 (Hermes Fase 0.8 context)

## Context

ADR-0007 mandated heuristic fallback to ensure VNBOT works without any LLM
dependency. ADR-0009 added Hermes (background review, skill creation, memory
curation) which also depends on LLM availability.

The original implementation only supported Z.AI (glm-4.6, keyless) as the LLM
provider. Users requested support for other cloud providers:
- OpenAI (gpt-4o, gpt-4o-mini)
- Anthropic (claude-3-5-sonnet, claude-3-5-haiku)
- Google Gemini (gemini-1.5-pro, gemini-1.5-flash)
- Ollama (local, llama3.2, qwen2.5)

Each provider has different strengths: OpenAI/Anthropic for complex reasoning,
Gemini for long-context, Z.AI for free keyless usage, Ollama for fully offline.

## Decision

Implement multi-LLM provider support with **chain fallback**:

### 1. Provider abstraction (`services/api/app/infrastructure/llm/providers.py`)

`ProviderConfig` dataclass captures per-provider settings:
- `name`, `base_url`, `model`, `api_key`
- `api_shape`: `"openai"` (OpenAI-compatible) or `"anthropic"` (native Messages API)
- `enabled`: whether the provider has required credentials
- `timeout`, `max_tokens`, `temperature`

`get_provider_configs()` returns all 5 providers in priority order. A provider
is `enabled` if:
- It has an API key in env vars (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`)
- OR it's keyless (Z.AI, Ollama)
- AND `LLM_PROVIDER` env var is `"auto"` OR matches the provider name

### 2. Chain fallback (`call_with_chain_fallback()`)

When parsing user input, the router tries providers in priority order:
1. **zai** (glm-4.6) — default, keyless
2. **openai** (gpt-4o-mini) — if `OPENAI_API_KEY` set
3. **anthropic** (claude-3-5-haiku) — if `ANTHROPIC_API_KEY` set
4. **gemini** (gemini-1.5-flash) — if `GEMINI_API_KEY` set
5. **ollama** (llama3.2) — local, if `OLLAMA_HOST` reachable
6. **heuristics** (no LLM) — ADR-0007 mandatory fallback

The first provider that returns valid content wins. If all LLMs fail, the
caller (`chat.py`) falls back to heuristic parsing.

`ChainResult` records which provider was used, tokens consumed, and per-provider
errors for debugging.

### 3. API shapes

- **OpenAI-compatible** (`api_shape="openai"`): Z.AI, OpenAI, Gemini (via
  OpenAI-compat endpoint), Ollama. All use `/chat/completions` with the same
  payload shape.
- **Anthropic native** (`api_shape="anthropic"`): uses `/v1/messages` with
  `system` as a top-level field (not a message) and `x-api-key` header.

### 4. Configuration via env vars

```bash
# Provider selection: "auto" tries all enabled providers in priority order
LLM_PROVIDER=auto  # default

# Z.AI (keyless, default)
LLM_ZAI_BASE_URL=https://api.z.ai/v1
LLM_ZAI_MODEL=glm-4.6
LLM_ZAI_API_KEY=  # optional, only for rate-limit-free tier

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini  # default
OPENAI_BASE_URL=  # optional, for Azure OpenAI or proxies

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-haiku-20241022
ANTHROPIC_BASE_URL=  # optional

# Google Gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash
GEMINI_BASE_URL=  # optional, defaults to OpenAI-compat endpoint

# Ollama (local)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 5. New API endpoints (`/api/v1/llm/`)

- `GET /api/v1/llm/providers` — list all providers with status (enabled, has_api_key, model)
- `POST /api/v1/llm/test` — test a specific provider with a sample prompt

The frontend uses these to show the user which providers are available and
let them test connectivity.

## Consequences

### Positive

- **Flexibility**: user can plug in any of 5 providers (or mix them)
- **Resilience**: if Z.AI is down, OpenAI/Anthropic/etc. take over automatically
- **Cost control**: free Z.AI default; user can choose paid providers when needed
- **Local mode**: Ollama enables fully offline operation (ADR-0008 local-first)
- **No vendor lock-in**: providers are interchangeable, all behind same interface
- **Easy to extend**: adding a new provider = adding a `ProviderConfig` entry

### Negative

- **Complexity**: more code paths to test (5 providers × 2 API shapes)
- **Token cost tracking**: each provider reports tokens differently; we use
  `total_tokens` from OpenAI-compat, sum of input+output for Anthropic
- **Latency on failure**: if primary provider times out, user waits up to 15s
  before fallback kicks in. Mitigated by short timeouts (15s default, 30s Ollama)

### Neutral

- **No provider preferences per task**: all parsing goes through the same chain.
  Future enhancement: route specific intents to specific providers (e.g., use
  Anthropic for complex reasoning, Gemini for long-context).

## Implementation

### Files added/modified

- `services/api/app/infrastructure/llm/providers.py` (NEW, ~280 LOC)
  - `ProviderConfig` dataclass
  - `get_provider_configs()` — returns all 5 providers
  - `get_enabled_providers()` — filters by `enabled=True`
  - `list_available_providers()` — for the API endpoint
  - `call_provider()` — calls one provider (dispatches by api_shape)
  - `_call_openai_compatible()` — Z.AI/OpenAI/Gemini/Ollama
  - `_call_anthropic()` — Anthropic native Messages API
  - `call_with_chain_fallback()` — tries providers in order, returns `ChainResult`

- `services/api/app/infrastructure/llm/router.py` (MODIFIED)
  - `parse_with_llm()` now calls `call_with_chain_fallback()` instead of
    hard-coded Z.AI call
  - `SYSTEM_PROMPT_TEMPLATE` unchanged — works with any provider
  - `LLMResult` unchanged — provider-agnostic

- `services/api/app/infrastructure/llm/__init__.py` (MODIFIED)
  - Exports `ProviderConfig`, `ChainResult`, `call_provider`, etc.

- `services/api/app/api/v1/llm.py` (NEW, ~110 LOC)
  - `GET /api/v1/llm/providers` — list providers
  - `POST /api/v1/llm/test` — test single provider

- `services/api/app/config.py` (MODIFIED)
  - `llm_provider` Literal now includes `"auto"` (default) + `"gemini"`

- `services/api/app/api/v1/__init__.py` (MODIFIED)
  - Registers `llm.router` under `/api/v1`

## Verification

```
✅ 5 providers configured: zai (enabled), openai, anthropic, gemini, ollama (enabled)
✅ Auto-mode: tries zai first, falls back to ollama if zai fails
✅ Typecheck passes (tsc --noEmit on web; py_compile on api)
✅ Backend starts cleanly with all routers loaded
✅ GET /api/v1/llm/providers returns provider list with status
✅ POST /api/v1/llm/test works for any enabled provider
✅ Heuristic fallback still works (ADR-0007) if all LLMs fail
```

## Future Work

- **Provider routing by intent**: use different providers for different tasks
  (e.g., Gemini for long-context queries, Anthropic for complex reasoning)
- **Cost tracking**: log per-provider token usage for cost analysis
- **Streaming responses**: support `stream: true` for faster first-token latency
- **Rate limit handling**: per-provider rate limit tracking + backoff
- **Frontend UI**: Settings panel to enable/disable providers + enter API keys
