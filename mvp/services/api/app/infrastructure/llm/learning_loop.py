"""VNBOT API — Hermes Learning Loop stub (ADR-0009).

Per ADR-0009 Track 2: after each chat response, spawn a background
LLM call that reviews the transcript and decides what to persist.
This is a STUB for Fase 0.7 — not active yet.

The stub is here so the architecture is ready when we implement
the full learning loop in Fase 0.7.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger("vnbot.api.learning")

# This is the prompt that the background review fork will use
REVIEW_PROMPT = """Eres el módulo de aprendizaje de VNBOT. Revisa esta conversación y decide:

1. ¿Hay algo que valga la pena recordar como memoria? (máximo 1-2 items)
2. ¿Se puede crear o mejorar una skill? (patrón repetido, recovery de error, etc.)
3. ¿Hay información del usuario que actualizar en USER.md?

Responde SOLO con un JSON:
{
  "memories_to_save": [
    {"content": "contenido a guardar", "type": "note|preference|event", "confidence": 0.0-1.0}
  ],
  "skill_to_create": null,
  "skill_to_patch": null,
  "user_info_update": null,
  "nothing_to_learn": true
}

Reglas:
- Si no hay nada que aprender, devuelve {"nothing_to_learn": true}
- No guardes conversación casual, solo datos persistentes
- Confidence < 0.5 si no estás seguro
- Máximo 2 memorias por revisión (curación sobre acumulación)"""


@dataclass
class LearningResult:
    """Result of the background learning review."""
    memories_to_save: list[dict]
    skill_to_create: dict | None
    skill_to_patch: dict | None
    user_info_update: dict | None
    nothing_to_learn: bool


async def background_review(
    user_input: str,
    assistant_response: str,
    intent: str,
    used_llm: bool,
) -> LearningResult | None:
    """Background review fork — runs AFTER the user-visible response.

    This is a STUB. In Fase 0.7, this will:
    1. Spawn a separate LLM call with the transcript + REVIEW_PROMPT
    2. Use a narrow tool whitelist (memory.save, skill.create, skill.patch only)
    3. Never block the user — always async
    4. Log what was learned for audit

    For now, just log that the review would happen.
    """
    logger.debug(
        f"[STUB] Background review would run for intent={intent}, "
        f"used_llm={used_llm}, input_length={len(user_input)}"
    )
    return None


async def memory_curation() -> None:
    """Periodic memory curation job.

    This is a STUB. In Fase 0.7, this will:
    1. Read current MEMORY.md + recent activity
    2. Decide what to keep, compress, or remove
    3. Maintain ~3.5KB cap on prompt memory
    4. Run every 6 hours or 50 interactions
    """
    logger.debug("[STUB] Memory curation would run here")


async def skill_creation_check(
    tool_calls_count: int,
    error_recovered: bool,
    user_corrected: bool,
) -> bool:
    """Check if a skill should be created from the current interaction.

    Triggers (per ADR-0009):
    - ≥5 tool calls in a single operation
    - Error recovery (agent failed then succeeded)
    - User correction ("no, quería decir...")
    - Novel successful workflow

    This is a STUB — just returns the trigger condition.
    """
    if tool_calls_count >= 5:
        logger.info(f"[STUB] Skill creation trigger: {tool_calls_count} tool calls")
        return True
    if error_recovered:
        logger.info("[STUB] Skill creation trigger: error recovery")
        return True
    if user_corrected:
        logger.info("[STUB] Skill creation trigger: user correction")
        return True
    return False
