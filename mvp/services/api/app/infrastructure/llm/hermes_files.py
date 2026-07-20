"""VNBOT API — Hermes persistence files (USER.md + MEMORY.md).

Per ADR-0009 §3.2 (Hermes integration):
- USER.md: persistent user facts (name, preferences, key context)
- MEMORY.md: working memory cap'd at ~3.5KB for LLM prompt context

These files are materialized from the database (memory_nodes table) and
used as system prompt context for future LLM calls. The cap on MEMORY.md
is enforced by memory_curation() in learning_loop.py.

Files are stored under the workspace data dir:
    ~/.vnbot/workspaces/<workspace_id>/USER.md
    ~/.vnbot/workspaces/<workspace_id>/MEMORY.md
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import get_settings
from ..db.models import MemoryNode, User, Workspace

logger = logging.getLogger("vnbot.api.hermes_files")

# Default content for fresh USER.md / MEMORY.md
DEFAULT_USER_MD = """# Perfil del Usuario

<!-- VNBOT mantiene este archivo con hechos verificables sobre el usuario.
     Hermes actualiza este archivo cuando detecta nueva información persistente. -->

## Información Básica
- Nombre: (por definir)
- Zona horaria: America/Caracas
- Idioma: es

## Preferencias Conocidas
<!-- Lista de preferencias explícitas que el usuario ha compartido -->

## Contexto de Proyectos
<!-- Proyectos activos, contexto de trabajo, etc. -->
"""

DEFAULT_MEMORY_MD = """# Memoria de Trabajo

<!-- VNBOT mantiene este archivo con recuerdos activos.
     Cap ~3.5KB. La curación periódica comprime/elimina entradas viejas. -->

## Hechos Recientes
<!-- Eventos, notas, contexto reciente -->

## Preferencias Activas
<!-- Preferencias que afectan el comportamiento actual -->
"""


def _workspace_dir(workspace_id: str) -> Path:
    """Return the workspace data directory, creating it if needed."""
    settings = get_settings()
    # Use storage_local_path as the base for workspace data (consistent with file storage)
    base = Path(settings.storage_local_path).expanduser() / "workspaces" / workspace_id
    base.mkdir(parents=True, exist_ok=True)
    return base


def user_md_path(workspace_id: str) -> Path:
    """Path to USER.md for the given workspace."""
    return _workspace_dir(workspace_id) / "USER.md"


def memory_md_path(workspace_id: str) -> Path:
    """Path to MEMORY.md for the given workspace."""
    return _workspace_dir(workspace_id) / "MEMORY.md"


def ensure_persistence_files(workspace_id: str) -> None:
    """Create USER.md and MEMORY.md with defaults if they don't exist."""
    user_path = user_md_path(workspace_id)
    if not user_path.exists():
        user_path.write_text(DEFAULT_USER_MD, encoding="utf-8")
        logger.info(f"Created {user_path}")

    mem_path = memory_md_path(workspace_id)
    if not mem_path.exists():
        mem_path.write_text(DEFAULT_MEMORY_MD, encoding="utf-8")
        logger.info(f"Created {mem_path}")


async def materialize_memory_md(
    db: AsyncSession,
    workspace_id: str,
    cap_bytes: int = 3500,
) -> str:
    """Regenerate MEMORY.md from the database (memory_nodes table).

    Selects the most confident, most recent active memories, respecting the
    byte cap. Writes the file and returns the content.
    """
    # Fetch active memories ordered by confidence desc, then updated_at desc
    stmt = (
        select(MemoryNode)
        .where(
            MemoryNode.workspace_id == workspace_id,
            MemoryNode.status == "active",
        )
        .order_by(MemoryNode.confidence.desc(), MemoryNode.updated_at.desc())
        .limit(100)  # safety bound
    )
    result = await db.execute(stmt)
    nodes = result.scalars().all()

    lines = ["# Memoria de Trabajo", ""]
    current_bytes = sum(len(l.encode("utf-8")) + 1 for l in lines)
    included = 0

    for node in nodes:
        entry = f"- **{node.label}** (conf={node.confidence:.2f}, type={node.type}): {(node.content_ciphertext or '')[:200]}"
        entry_bytes = len(entry.encode("utf-8")) + 1
        if current_bytes + entry_bytes > cap_bytes:
            continue  # skip — would exceed cap
        lines.append(entry)
        current_bytes += entry_bytes
        included += 1

    if included == 0:
        lines.append("<!-- (sin memorias activas bajo el cap) -->")

    lines.append("")
    lines.append(f"<!-- Materializado: {datetime.now(timezone.utc).isoformat()} | {included} memorias | {current_bytes}B -->")

    content = "\n".join(lines)
    mem_path = memory_md_path(workspace_id)
    mem_path.write_text(content, encoding="utf-8")
    logger.info(f"Materialized MEMORY.md: {included} memories, {current_bytes}B")
    return content


async def materialize_user_md(
    db: AsyncSession,
    workspace_id: str,
) -> str:
    """Regenerate USER.md from the database (users + workspace tables).

    Pulls user facts (name, timezone, locale) and preference memories.
    """
    # Load user + workspace
    ws = await db.get(Workspace, workspace_id)
    user = await db.get(User, ws.owner_user_id) if ws else None

    # Load preference-type memories
    pref_stmt = (
        select(MemoryNode)
        .where(
            MemoryNode.workspace_id == workspace_id,
            MemoryNode.status == "active",
            MemoryNode.type == "preference",
        )
        .order_by(MemoryNode.confidence.desc(), MemoryNode.updated_at.desc())
        .limit(20)
    )
    pref_result = await db.execute(pref_stmt)
    pref_nodes = pref_result.scalars().all()

    lines = [
        "# Perfil del Usuario",
        "",
        "## Información Básica",
        f"- Nombre: {user.display_name if user else '(por definir)'}",
        f"- Zona horaria: {user.timezone if user else 'UTC'}",
        f"- Idioma: {user.locale if user else 'es'}",
        "",
        "## Preferencias Conocidas",
    ]

    if pref_nodes:
        for node in pref_nodes:
            content = (node.content_ciphertext or "").strip()
            if content:
                lines.append(f"- **{node.label}**: {content[:200]}")
    else:
        lines.append("<!-- (sin preferencias explícitas registradas aún) -->")

    lines.append("")
    lines.append(f"<!-- Materializado: {datetime.now(timezone.utc).isoformat()} | {len(pref_nodes)} preferencias -->")

    content = "\n".join(lines)
    user_path = user_md_path(workspace_id)
    user_path.write_text(content, encoding="utf-8")
    logger.info(f"Materialized USER.md: {len(pref_nodes)} preferences")
    return content


async def read_user_md(workspace_id: str) -> str:
    """Read USER.md, returning defaults if file doesn't exist."""
    ensure_persistence_files(workspace_id)
    return user_md_path(workspace_id).read_text(encoding="utf-8")


async def read_memory_md(workspace_id: str) -> str:
    """Read MEMORY.md, returning defaults if file doesn't exist."""
    ensure_persistence_files(workspace_id)
    return memory_md_path(workspace_id).read_text(encoding="utf-8")
