"""VNBOT API — LLM Router with chain fallback (ADR-0007 + ADR-0012).

Per ADR-0007: heuristic fallback is mandatory before depending on LLM.
Per ADR-0012: multiple cloud LLM providers supported with chain fallback.
  Priority order (configurable via LLM_PROVIDER):
    1. zai (default, keyless — glm-4.6)
    2. openai (gpt-4o-mini)
    3. anthropic (claude-3-5-haiku)
    4. gemini (gemini-1.5-flash)
    5. ollama (local — llama3.2)
    6. heuristic fallback (no LLM)

The router tries LLM providers in order until one succeeds, then falls back
to heuristics if all LLMs are unavailable.

Per ADR-0011 (Fase 0.8): the system prompt includes USER.md + MEMORY.md
context so the LLM has access to long-term user facts and working memory.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from ...config import get_settings

logger = logging.getLogger("vnbot.api.llm")

SYSTEM_PROMPT_TEMPLATE = """Eres el parser de VNBOT, un asistente personal. Analiza el input del usuario y devuelve un JSON con la intención detectada y los datos extraídos.

Intenciones posibles:
- create_reminder: el usuario quiere ser recordado algo en una fecha/hora
- create_memory: el usuario quiere guardar un dato o información
- create_task: el usuario tiene que hacer algo
- create_list_item: el usuario quiere añadir algo a una lista
- query_memories: el usuario pregunta qué recuerdas
- list_reminders: el usuario pregunta por sus recordatorios
- complete_reminder: el usuario indica que ya hizo algo
- delete_memory: el usuario quiere olvidar algo
- unknown: no se puede determinar la intención

Devuelve SOLO un JSON válido, sin markdown, con esta estructura:
{{
  "intent": "create_reminder|create_memory|create_task|create_list_item|query_memories|list_reminders|complete_reminder|delete_memory|unknown",
  "confidence": 0.0-1.0,
  "reminder": {{
    "title": "título corto del recordatorio",
    "due_at": "ISO datetime en UTC, o null si no se puede determinar",
    "timezone": "zona horaria inferida",
    "recurrence": "none|daily|weekly|monthly|yearly"
  }},
  "memory": {{
    "content": "contenido de la memoria",
    "type": "note|event|preference|task|contact",
    "tags": ["tag1", "tag2"],
    "relations": [
      {{
        "target_label": "título de una memoria existente que se relaciona",
        "relation_type": "KNOWS|RELATED_TO|PREFERS|WORKS_ON|DEPENDS_ON|HAPPENS_AT|REMINDER_FOR|LOCATED_AT|MENTIONED_IN",
        "confidence": 0.0-1.0
      }}
    ]
  }},
  "suggestion": "mensaje amigable si intent=unknown"
}}

Reglas:
- Si la fecha es ambigua, usa tu mejor juicio basado en el contexto
- "mañana" = el día siguiente a las 9:00 AM
- "tarde" = 15:00, "noche" = 20:00
- Para memorias, extrae el contenido limpio sin el comando inicial
- relations: detecta si la nueva memoria se relaciona con algo que el usuario probablemente ya tiene guardado (personas, lugares, proyectos). Si no hay relación clara, devuelve array vacío.
- Confidence < 0.5 si no estás seguro
- Devuelve SOLO el JSON, nada más

## Contexto del usuario (USER.md)
{user_md}

## Memoria de trabajo (MEMORY.md)
{memory_md}"""


@dataclass
class LLMResult:
    """Result from LLM parsing."""

    intent: str
    confidence: float
    reminder: dict[str, Any] | None = None
    memory: dict[str, Any] | None = None
    suggestion: str | None = None
    raw_response: str | None = None
    used_llm: bool = True


def _build_system_prompt(workspace_id: str = "00000000-0000-0000-0000-000000000001") -> str:
    """Build the system prompt with USER.md + MEMORY.md context injected.

    Per ADR-0011 Fase 0.8: the LLM gets long-term user context so it can
    personalize parsing. Falls back to a no-context prompt if files are
    unavailable (e.g., on first run, or if materialize has never been called).

    Uses synchronous file reads — these are tiny (~3.5KB) and cached by the OS.
    """
    try:
        from .hermes_files import read_memory_md, read_user_md, ensure_persistence_files
        import asyncio

        # Ensure files exist (creates defaults if missing)
        ensure_persistence_files(workspace_id)

        # Run async reads synchronously (we're in a sync context here)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're inside an async context — can't use asyncio.run, use sync fallback
                user_md = _read_file_sync(workspace_id, "USER.md")
                memory_md = _read_file_sync(workspace_id, "MEMORY.md")
            else:
                user_md = asyncio.run(read_user_md(workspace_id))
                memory_md = asyncio.run(read_memory_md(workspace_id))
        except RuntimeError:
            # No event loop — use sync reads
            user_md = _read_file_sync(workspace_id, "USER.md")
            memory_md = _read_file_sync(workspace_id, "MEMORY.md")

        # Truncate to avoid token bloat
        if len(user_md) > 2000:
            user_md = user_md[:2000] + "\n<!-- (truncated) -->"
        if len(memory_md) > 3500:
            memory_md = memory_md[:3500] + "\n<!-- (truncated) -->"

        return SYSTEM_PROMPT_TEMPLATE.format(
            user_md=user_md,
            memory_md=memory_md,
        )
    except Exception as e:
        logger.warning(f"Failed to build context-aware system prompt: {e} — using bare prompt")
        return SYSTEM_PROMPT_TEMPLATE.format(
            user_md="<!-- (no context available) -->",
            memory_md="<!-- (no context available) -->",
        )


def _read_file_sync(workspace_id: str, filename: str) -> str:
    """Synchronous read of USER.md or MEMORY.md."""
    from pathlib import Path
    from ...config import get_settings
    settings = get_settings()
    path = Path(settings.storage_local_path).expanduser() / "workspaces" / workspace_id / filename
    if not path.exists():
        return f"<!-- (file {filename} does not exist yet) -->"
    return path.read_text(encoding="utf-8")


async def parse_with_llm(
    text: str,
    timezone: str = "America/Caracas",
    workspace_id: str = "00000000-0000-0000-0000-000000000001",
) -> LLMResult | None:
    """Parse user input using LLM with chain fallback (ADR-0007 + ADR-0012).

    Returns None if ALL LLM providers fail (caller should fall back to heuristics).

    Per ADR-0011 Fase 0.8: includes USER.md + MEMORY.md context in system prompt.
    Per ADR-0012: tries providers in priority order until one succeeds.
    """
    settings = get_settings()

    # ─── Build context-aware system prompt (Fase 0.8) ───
    system_prompt = _build_system_prompt(workspace_id)
    user_message = f"Zona horaria del usuario: {timezone}\n\nInput: {text}"

    # ─── Chain fallback across LLM providers (ADR-0012) ───
    from .providers import call_with_chain_fallback

    chain = await call_with_chain_fallback(
        system_prompt=system_prompt,
        user_message=user_message,
        preferred_provider=settings.llm_provider if settings.llm_provider != "zai" else None,
    )

    if chain.content is None:
        # All providers failed — caller falls back to heuristics
        if chain.errors:
            logger.warning(
                f"[LLM] All providers failed: {chain.errors} — falling back to heuristics"
            )
        return None

    # ─── Parse the response (same logic regardless of provider) ───
    content = chain.content.strip()

    # Strip markdown code fences if present
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        logger.warning(
            f"[LLM] {chain.provider_used} returned non-JSON: {content[:200]} — falling back"
        )
        return None

    return LLMResult(
        intent=parsed.get("intent", "unknown"),
        confidence=float(parsed.get("confidence", 0.5)),
        reminder=parsed.get("reminder"),
        memory=parsed.get("memory"),
        suggestion=parsed.get("suggestion"),
        raw_response=content,
        used_llm=True,
    )
