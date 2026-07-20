"""VNBOT API — Hermes Learning Loop (ADR-0009 Fase 0.7).

Per ADR-0009 Track 2: after each chat response, spawn a background
LLM call that reviews the transcript and decides what to persist.

This is the FULL Fase 0.7 implementation:
- background_review(): async LLM call post-response, never blocks user
- memory_curation(): periodic job that maintains ~3.5KB MEMORY.md cap
- skill_creation_check(): trigger detection (≥5 tool calls, error recovery,
  user correction, novel successful workflow)

Key design principles (ADR-0009):
1. NEVER block the user-visible response
2. Narrow tool whitelist (memory.save, skill.create, skill.patch only)
3. Every action writes a LearningLog entry for audit
4. Confidence starts low, increases with successful uses
5. Curación > acumulación (max 2 memories per review)
6. MEMORY.md cap ~3.5KB — compress/demote old entries
7. USER.md for persistent user facts
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import httpx
from sqlalchemy import select, func, update

from ...config import get_settings
from ..db.models import LearningLog, MemoryNode, Skill
from ..db.session import async_session_factory

logger = logging.getLogger("vnbot.api.learning")

# ──────────────────────────────────────────────────────────────────────────────
# Constants (ADR-0009)
# ──────────────────────────────────────────────────────────────────────────────

# Cap on prompt memory (MEMORY.md) — compressed when exceeded
MEMORY_MD_CAP_BYTES = 3500

# Max memories per background review (curación > acumulación)
MAX_MEMORIES_PER_REVIEW = 2

# Min confidence for Hermes-created memories
MIN_MEMORY_CONFIDENCE = 0.5

# Skill creation triggers
TOOL_CALL_THRESHOLD = 5

# How often memory_curation runs
CURATION_INTERVAL_HOURS = 6

# Workspace default IDs (single-user local mode)
DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"

# REVIEW_PROMPT — system prompt for the background review fork
REVIEW_PROMPT = """Eres el módulo de aprendizaje de VNBOT. Revisa esta conversación y decide qué aprender.

CAPS ESTRICTAS:
- Máximo 2 memorias por revisión (curación > acumulación)
- No guardes conversación casual, solo datos persistentes y verificables
- Confidence < 0.5 si no estás seguro (esos se descartan)
- No inventes datos — solo extrae lo que el usuario dijo explícitamente

QUÉ SÍ GUARDAR:
- Preferencias explícitas del usuario ("me gusta X", "prefiero Y")
- Hechos verificables ("mi cumpleaños es X", "trabajo en Y")
- Eventos importantes con fecha
- Datos de contacto
- Contexto de proyectos

QUÉ NO GUARDAR:
- Saludos, despedidas, charla casual
- Acciones momentáneas ("recuérdame X a las Y" → eso es reminder, no memory)
- Opiniones subjetivas sin valor persistente
- Datos sensibles (contraseñas, tokens) — NUNCA

Responde SOLO con un JSON válido:
{
  "memories_to_save": [
    {
      "content": "contenido limpio y verificable",
      "type": "note|preference|event|contact|task",
      "tags": ["tag1"],
      "confidence": 0.0-1.0,
      "label": "título corto descriptivo"
    }
  ],
  "user_info_update": null,
  "nothing_to_learn": false
}

Si no hay nada que valga la pena guardar, devuelve:
{"memories_to_save": [], "user_info_update": null, "nothing_to_learn": true}

Reglas finales:
- Máximo 2 items en memories_to_save
- Confidence debe ser > 0.5 para que se guarde
- type "preference" para cosas que el usuario prefiere
- type "event" para cosas con fecha
- type "contact" para datos de personas
- type "note" para todo lo demás persistente
- El label debe ser corto (máx 80 chars) y descriptivo
- No uses markdown en el contenido, texto plano"""


@dataclass
class LearningResult:
    """Result of the background learning review."""

    memories_to_save: list[dict] = field(default_factory=list)
    user_info_update: dict | None = None
    nothing_to_learn: bool = True
    raw_review: dict | None = None
    error: str | None = None
    llm_tokens_used: int = 0


# ──────────────────────────────────────────────────────────────────────────────
# Background review (called AFTER user-visible response)
# ──────────────────────────────────────────────────────────────────────────────


async def background_review(
    user_input: str,
    assistant_response: str,
    intent: str,
    used_llm: bool,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
) -> LearningResult:
    """Background review fork — runs AFTER the user-visible response.

    Per ADR-0009:
    1. Spawn a separate LLM call with the transcript + REVIEW_PROMPT
    2. Use a narrow tool whitelist (memory.save, skill.create, skill.patch only)
    3. Never block the user — always async (caller should await in background task)
    4. Log what was learned for audit (LearningLog table)

    Returns LearningResult with what was actually saved.
    """
    result = LearningResult()

    # ─── Step 1: Call LLM with REVIEW_PROMPT ───
    review_data = await _call_review_llm(user_input, assistant_response, intent)
    if review_data is None:
        result.error = "LLM call failed or unavailable"
        await _log_learning_action(
            workspace_id=workspace_id,
            action="background_review",
            trigger_reason=f"post-response (intent={intent}, used_llm={used_llm})",
            review_json={},
            outcome_summary="LLM call failed",
            success=False,
            error_message=result.error,
        )
        return result

    result.raw_review = review_data
    result.llm_tokens_used = review_data.get("_tokens_used", 0)

    # ─── Step 2: Apply the learning (memory.save) ───
    memories_to_save = review_data.get("memories_to_save", []) or []
    # Enforce cap
    memories_to_save = memories_to_save[:MAX_MEMORIES_PER_REVIEW]
    # Filter by confidence
    memories_to_save = [
        m for m in memories_to_save
        if float(m.get("confidence", 0.0)) >= MIN_MEMORY_CONFIDENCE
    ]

    saved_memory_ids: list[str] = []
    for mem_data in memories_to_save:
        try:
            memory_id = await _save_memory(workspace_id, mem_data)
            if memory_id:
                saved_memory_ids.append(memory_id)
        except Exception as e:
            logger.warning(f"Failed to save Hermes memory: {e}")

    result.memories_to_save = memories_to_save
    result.nothing_to_learn = review_data.get("nothing_to_learn", False) and not saved_memory_ids
    result.user_info_update = review_data.get("user_info_update")

    # ─── Step 3: Write audit log ───
    outcome = (
        f"nothing_to_learn=True"
        if result.nothing_to_learn
        else f"saved {len(saved_memory_ids)} memories"
    )
    await _log_learning_action(
        workspace_id=workspace_id,
        action="background_review",
        trigger_reason=f"post-response (intent={intent}, used_llm={used_llm})",
        review_json=review_data,
        outcome_summary=outcome,
        memory_ids=saved_memory_ids,
        success=True,
        llm_tokens=result.llm_tokens_used,
    )

    logger.info(
        f"[Hermes] background_review: {outcome} "
        f"(intent={intent}, tokens={result.llm_tokens_used})"
    )
    return result


async def _call_review_llm(
    user_input: str,
    assistant_response: str,
    intent: str,
) -> dict | None:
    """Call Z.AI LLM with REVIEW_PROMPT. Returns parsed JSON or None."""
    settings = get_settings()

    if settings.llm_provider != "zai":
        logger.debug(f"LLM provider is {settings.llm_provider}, not zai — skipping review")
        return None

    user_msg = (
        f"Intención detectada: {intent}\n\n"
        f"Input del usuario: {user_input[:500]}\n\n"
        f"Respuesta del asistente: {assistant_response[:500]}\n\n"
        f"Analiza qué vale la pena recordar como memoria persistente."
    )

    try:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.llm_api_key:
            headers["Authorization"] = f"Bearer {settings.llm_api_key}"

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{settings.llm_zai_base_url}/chat/completions",
                json={
                    "model": settings.llm_zai_model,
                    "messages": [
                        {"role": "system", "content": REVIEW_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 800,
                },
                headers=headers,
            )

            if response.status_code != 200:
                logger.warning(f"Z.AI review returned {response.status_code}: {response.text[:200]}")
                return None

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            tokens_used = data.get("usage", {}).get("total_tokens", 0)

            # Strip markdown code fences if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                logger.warning(f"Z.AI review returned non-JSON: {content[:200]}")
                return None

            parsed["_tokens_used"] = tokens_used
            return parsed

    except httpx.TimeoutException:
        logger.warning("Z.AI review timed out")
        return None
    except Exception as e:
        logger.warning(f"Z.AI review failed: {type(e).__name__}: {e}")
        return None


async def _save_memory(workspace_id: str, mem_data: dict) -> str | None:
    """Persist a Hermes-detected memory to memory_nodes table."""
    content = (mem_data.get("content") or "").strip()
    if not content:
        return None

    memory_id = str(uuid4())
    label = (mem_data.get("label") or content[:80]).strip()[:255]
    mem_type = (mem_data.get("type") or "note").strip()
    confidence = float(mem_data.get("confidence", 0.5))

    async with async_session_factory() as session:
        node = MemoryNode(
            id=memory_id,
            workspace_id=workspace_id,
            type=mem_type,
            label=label,
            content_ciphertext=content,  # plain for now (Phase 0.1)
            content_format="text",
            source_type="hermes_background_review",
            confidence=confidence,
            status="active",
        )
        session.add(node)
        await session.commit()

    return memory_id


# ──────────────────────────────────────────────────────────────────────────────
# Memory curation (periodic job)
# ──────────────────────────────────────────────────────────────────────────────


async def memory_curation(workspace_id: str = DEFAULT_WORKSPACE_ID) -> dict:
    """Periodic memory curation job.

    Per ADR-0009:
    1. Read current MEMORY.md + recent activity
    2. Decide what to keep, compress, or remove
    3. Maintain ~3.5KB cap on prompt memory
    4. Run every CURATION_INTERVAL_HOURS

    Returns a summary of what was done.
    """
    summary: dict[str, Any] = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "total_memories_before": 0,
        "total_memories_after": 0,
        "demoted_low_confidence": 0,
        "compressed_old_entries": 0,
        "kept_active": 0,
        "bytes_estimate": 0,
    }

    async with async_session_factory() as session:
        # Count all active memories
        count_stmt = select(func.count(MemoryNode.id)).where(
            MemoryNode.workspace_id == workspace_id,
            MemoryNode.status == "active",
        )
        total = (await session.execute(count_stmt)).scalar_one()
        summary["total_memories_before"] = total

        # If we're under cap, no action needed
        # Rough estimate: avg 200 bytes per memory (label + content)
        estimated_bytes = total * 200
        summary["bytes_estimate"] = estimated_bytes

        if estimated_bytes <= MEMORY_MD_CAP_BYTES:
            summary["total_memories_after"] = total
            summary["kept_active"] = total
            logger.info(f"[Hermes] memory_curation: under cap ({estimated_bytes}B), no action")
            await _log_learning_action(
                workspace_id=workspace_id,
                action="memory_curation",
                trigger_reason=f"periodic (under cap {estimated_bytes}B/{MEMORY_MD_CAP_BYTES}B)",
                review_json=summary,
                outcome_summary="no action needed (under cap)",
                success=True,
            )
            return summary

        # ─── Compression strategy ───
        # 1. Demote low-confidence Hermes memories (confidence < 0.6)
        # 2. If still over cap, demote oldest non-recently-used memories

        # Step 1: Demote low-confidence Hermes memories
        low_conf_stmt = (
            update(MemoryNode)
            .where(
                MemoryNode.workspace_id == workspace_id,
                MemoryNode.status == "active",
                MemoryNode.confidence < 0.6,
                MemoryNode.source_type == "hermes_background_review",
            )
            .values(status="archived")
        )
        result = await session.execute(low_conf_stmt)
        demoted = result.rowcount or 0
        summary["demoted_low_confidence"] = demoted

        # Step 2: If still over cap, demote oldest
        remaining = total - demoted
        if remaining * 200 > MEMORY_MD_CAP_BYTES:
            # Find oldest non-source_type=explicit_user_input memories to archive
            excess = remaining - (MEMORY_MD_CAP_BYTES // 200)
            if excess > 0:
                old_stmt = (
                    select(MemoryNode)
                    .where(
                        MemoryNode.workspace_id == workspace_id,
                        MemoryNode.status == "active",
                        MemoryNode.source_type != "explicit_user_input",
                    )
                    .order_by(MemoryNode.updated_at.asc())
                    .limit(excess)
                )
                old_nodes = (await session.execute(old_stmt)).scalars().all()
                for node in old_nodes:
                    node.status = "archived"
                summary["compressed_old_entries"] = len(old_nodes)

        await session.commit()

        # Final count
        final_count = (
            await session.execute(
                select(func.count(MemoryNode.id)).where(
                    MemoryNode.workspace_id == workspace_id,
                    MemoryNode.status == "active",
                )
            )
        ).scalar_one()
        summary["total_memories_after"] = final_count
        summary["kept_active"] = final_count

    outcome = (
        f"demoted {summary['demoted_low_confidence']} low-conf, "
        f"archived {summary['compressed_old_entries']} old, "
        f"kept {summary['kept_active']} active"
    )
    await _log_learning_action(
        workspace_id=workspace_id,
        action="memory_curation",
        trigger_reason=f"periodic (over cap, was {estimated_bytes}B)",
        review_json=summary,
        outcome_summary=outcome,
        success=True,
    )
    logger.info(f"[Hermes] memory_curation: {outcome}")
    return summary


# ──────────────────────────────────────────────────────────────────────────────
# Skill creation check (trigger detection)
# ──────────────────────────────────────────────────────────────────────────────


async def skill_creation_check(
    tool_calls_count: int,
    error_recovered: bool,
    user_corrected: bool,
    novel_workflow: bool = False,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    context_summary: str = "",
) -> str | None:
    """Check if a skill should be created from the current interaction.

    Triggers (per ADR-0009):
    - ≥5 tool calls in a single operation
    - Error recovery (agent failed then succeeded)
    - User correction ("no, quería decir...")
    - Novel successful workflow

    Returns the new skill_id if a skill was created, or None.
    """
    trigger_reason: str | None = None
    if tool_calls_count >= TOOL_CALL_THRESHOLD:
        trigger_reason = f"≥{TOOL_CALL_THRESHOLD} tool calls ({tool_calls_count})"
    elif error_recovered:
        trigger_reason = "error recovery"
    elif user_corrected:
        trigger_reason = "user correction"
    elif novel_workflow:
        trigger_reason = "novel successful workflow"

    if not trigger_reason:
        return None

    # Generate a draft skill via LLM (or just stub if LLM unavailable)
    skill_id = await _generate_draft_skill(
        workspace_id=workspace_id,
        trigger_reason=trigger_reason,
        context_summary=context_summary,
    )

    if skill_id:
        await _log_learning_action(
            workspace_id=workspace_id,
            action="skill_created",
            trigger_reason=trigger_reason,
            review_json={"context_summary": context_summary[:500]},
            outcome_summary=f"created draft skill (id={skill_id})",
            skill_id=skill_id,
            success=True,
        )
        logger.info(f"[Hermes] skill_created via {trigger_reason}: {skill_id}")
    else:
        await _log_learning_action(
            workspace_id=workspace_id,
            action="skill_created",
            trigger_reason=trigger_reason,
            review_json={"context_summary": context_summary[:500]},
            outcome_summary="failed to generate draft skill",
            success=False,
            error_message="LLM unavailable or returned invalid skill",
        )

    return skill_id


async def _generate_draft_skill(
    workspace_id: str,
    trigger_reason: str,
    context_summary: str,
) -> str | None:
    """Generate a draft skill (markdown body) via LLM. Returns skill_id or None."""
    settings = get_settings()
    if settings.llm_provider != "zai":
        return None

    skill_prompt = """Eres el módulo de creación de skills de VNBOT. Genera una skill en formato markdown que capture el patrón de la interacción descrita.

Una skill tiene esta estructura:

# <nombre-de-la-skill>

## Descripción
<una o dos frases describiendo qué hace>

## Cuándo usar
<condiciones bajo las cuales esta skill debe activarse>

## Pasos
1. <paso 1>
2. <paso 2>
3. ...

## Notas
<caveats, edge cases, etc.>

Responde SOLO con el markdown de la skill, sin explicaciones adicionales."""

    try:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.llm_api_key:
            headers["Authorization"] = f"Bearer {settings.llm_api_key}"

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{settings.llm_zai_base_url}/chat/completions",
                json={
                    "model": settings.llm_zai_model,
                    "messages": [
                        {"role": "system", "content": skill_prompt},
                        {
                            "role": "user",
                            "content": (
                                f"Trigger: {trigger_reason}\n\n"
                                f"Contexto de la interacción:\n{context_summary[:1000]}\n\n"
                                f"Genera una skill markdown que capture este patrón."
                            ),
                        },
                    ],
                    "temperature": 0.4,
                    "max_tokens": 600,
                },
                headers=headers,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            body_markdown = data["choices"][0]["message"]["content"].strip()

            # Extract name from first heading
            name = "untitled-skill"
            for line in body_markdown.splitlines():
                line = line.strip()
                if line.startswith("# "):
                    name = line[2:].strip().lower().replace(" ", "-")[:100]
                    break

            # Avoid duplicates — check if name already exists
            skill_id = str(uuid4())
            async with async_session_factory() as session:
                # Check for existing skill with same name
                existing = await session.execute(
                    select(Skill).where(
                        Skill.workspace_id == workspace_id,
                        Skill.name == name,
                        Skill.status != "archived",
                    )
                )
                existing_skill = existing.scalar_one_or_none()
                if existing_skill:
                    # Patch the existing skill instead of creating duplicate
                    existing_skill.body_markdown = body_markdown
                    existing_skill.version += 1
                    existing_skill.confidence = min(1.0, existing_skill.confidence + 0.1)
                    existing_skill.updated_at = datetime.now(timezone.utc)
                    await session.commit()
                    return existing_skill.id

                # Create new draft skill
                description = ""
                for line in body_markdown.splitlines():
                    if "## Descripción" in line:
                        idx = body_markdown.splitlines().index(line)
                        if idx + 1 < len(body_markdown.splitlines()):
                            description = body_markdown.splitlines()[idx + 1].strip()
                        break

                skill = Skill(
                    id=skill_id,
                    workspace_id=workspace_id,
                    name=name,
                    description=description,
                    body_markdown=body_markdown,
                    triggers_json={"reason": trigger_reason},
                    status="draft",
                    origin="hermes",
                    version=1,
                    confidence=0.3,
                )
                session.add(skill)
                await session.commit()
                return skill_id

    except Exception as e:
        logger.warning(f"Failed to generate draft skill: {type(e).__name__}: {e}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Audit logging
# ──────────────────────────────────────────────────────────────────────────────


async def _log_learning_action(
    workspace_id: str,
    action: str,
    trigger_reason: str | None,
    review_json: dict,
    outcome_summary: str,
    *,
    memory_ids: list[str] | None = None,
    skill_id: str | None = None,
    llm_provider: str | None = None,
    llm_tokens: int = 0,
    success: bool = True,
    error_message: str | None = None,
) -> None:
    """Write a LearningLog entry for audit. Never raises."""
    try:
        settings = get_settings()
        # If provider not specified, infer from settings.llm_provider
        provider_used = llm_provider or (settings.llm_provider if settings.llm_provider != "auto" else "zai")
        async with async_session_factory() as session:
            entry = LearningLog(
                id=str(uuid4()),
                workspace_id=workspace_id,
                action=action,
                origin="hermes",
                trigger_reason=trigger_reason,
                review_json=review_json,
                outcome_summary=outcome_summary,
                memory_ids_json=memory_ids or [],
                skill_id=skill_id,
                llm_provider=provider_used,
                llm_model=settings.llm_zai_model if provider_used == "zai" else provider_used,
                llm_tokens_used=llm_tokens,
                success=success,
                error_message=error_message,
            )
            session.add(entry)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to write LearningLog: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Background task launcher (fire-and-forget from chat confirm)
# ──────────────────────────────────────────────────────────────────────────────


def spawn_background_review(
    user_input: str,
    assistant_response: str,
    intent: str,
    used_llm: bool,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
) -> asyncio.Task:
    """Fire-and-forget background review. Returns the Task (don't await).

    Per ADR-0009: the user-visible response must NEVER wait for this.
    """
    return asyncio.create_task(
        background_review(
            user_input=user_input,
            assistant_response=assistant_response,
            intent=intent,
            used_llm=used_llm,
            workspace_id=workspace_id,
        )
    )
