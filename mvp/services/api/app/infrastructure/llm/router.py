"""VNBOT API — LLM Router with Z.AI integration.

Per ADR-0007: heuristic fallback is mandatory before depending on LLM.
The router tries LLM first, falls back to heuristics on failure.

Z.AI (glm-4.6) requires NO API key — perfect for single-user local mode.
Uses OpenAI-compatible endpoint: https://api.z.ai/v1/chat/completions
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from ...config import get_settings

logger = logging.getLogger("vnbot.api.llm")

SYSTEM_PROMPT = """Eres el parser de VNBOT, un asistente personal. Analiza el input del usuario y devuelve un JSON con la intención detectada y los datos extraídos.

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
{
  "intent": "create_reminder|create_memory|create_task|create_list_item|query_memories|list_reminders|complete_reminder|delete_memory|unknown",
  "confidence": 0.0-1.0,
  "reminder": {
    "title": "título corto del recordatorio",
    "due_at": "ISO datetime en UTC, o null si no se puede determinar",
    "timezone": "zona horaria inferida",
    "recurrence": "none|daily|weekly|monthly|yearly"
  },
  "memory": {
    "content": "contenido de la memoria",
    "type": "note|event|preference|task|contact",
    "tags": ["tag1", "tag2"],
    "relations": [
      {
        "target_label": "título de una memoria existente que se relaciona",
        "relation_type": "KNOWS|RELATED_TO|PREFERS|WORKS_ON|DEPENDS_ON|HAPPENS_AT|REMINDER_FOR|LOCATED_AT|MENTIONED_IN",
        "confidence": 0.0-1.0
      }
    ]
  },
  "suggestion": "mensaje amigable si intent=unknown"
}

Reglas:
- Si la fecha es ambigua, usa tu mejor juicio basado en el contexto
- "mañana" = el día siguiente a las 9:00 AM
- "tarde" = 15:00, "noche" = 20:00
- Para memorias, extrae el contenido limpio sin el comando inicial
- relations: detecta si la nueva memoria se relaciona con algo que el usuario probablemente ya tiene guardado (personas, lugares, proyectos). Si no hay relación clara, devuelve array vacío.
- Confidence < 0.5 si no estás seguro
- Devuelve SOLO el JSON, nada más"""


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


async def parse_with_llm(text: str, timezone: str = "America/Caracas") -> LLMResult | None:
    """Parse user input using Z.AI LLM.

    Returns None if LLM is unavailable (caller should fall back to heuristics).
    """
    settings = get_settings()

    if settings.llm_provider != "zai":
        logger.debug(f"LLM provider is {settings.llm_provider}, not zai — skipping LLM")
        return None

    try:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.llm_api_key:
            headers["Authorization"] = f"Bearer {settings.llm_api_key}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{settings.llm_zai_base_url}/chat/completions",
                json={
                    "model": settings.llm_zai_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Zona horaria del usuario: {timezone}\n\nInput: {text}",
                        },
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
                headers=headers,
            )

            if response.status_code != 200:
                logger.warning(f"Z.AI returned {response.status_code}: {response.text[:200]}")
                return None

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            # Parse JSON from response (handle markdown code blocks)
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                logger.warning(f"Z.AI returned non-JSON: {content[:200]}")
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

    except httpx.TimeoutException:
        logger.warning("Z.AI request timed out — falling back to heuristics")
        return None
    except Exception as e:
        logger.warning(f"Z.AI request failed: {type(e).__name__}: {e}")
        return None
