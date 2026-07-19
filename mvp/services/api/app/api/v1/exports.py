"""VNBOT API — Export/Import endpoints.

POST /api/v1/export  — export all memories + reminders as encrypted JSON
POST /api/v1/import  — import encrypted JSON, recreate memories + reminders

Per docs/07 §33 (Export format) + docs/03 §33 (Backend MVP acceptance):
- Export produces a self-contained encrypted JSON bundle
- Schema versioned for forward compatibility
- Checksums for integrity verification
- Round-trip test: export → wipe → import → verify

Encryption: AES-256-GCM with PBKDF2 key derivation from user passphrase.
The passphrase is NEVER stored — only used transiently for encryption.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import get_workspace_id
from ...infrastructure.crypto.export import EncryptedPayload, decrypt_json, encrypt_json
from ...infrastructure.db.models import MemoryNode, Reminder
from ...infrastructure.db.session import get_db
from ...schemas.exports import ExportRequest, ExportResponse, ImportRequest, ImportResponse

router = APIRouter(tags=["exports"])

DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"

EXPORT_SCHEMA_VERSION = "1.0"


@router.post("/export", response_model=ExportResponse)
async def export_data(
    req: ExportRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ExportResponse:
    """Export all memories + reminders as encrypted JSON bundle.

    The passphrase is used to derive an AES-256 key via PBKDF2 (250k iter).
    The encrypted bundle is self-contained and can be imported on any device.
    """
    # Fetch all active memories
    mems_stmt = select(MemoryNode).where(
        MemoryNode.workspace_id == DEFAULT_WORKSPACE_ID,
        MemoryNode.status == "active",
    )
    memories = (await db.execute(mems_stmt)).scalars().all()

    # Fetch all reminders (active + completed)
    rems_stmt = select(Reminder).where(
        Reminder.workspace_id == DEFAULT_WORKSPACE_ID,
    )
    reminders = (await db.execute(rems_stmt)).scalars().all()

    # Build export payload
    export_data_dict = {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "workspace_id": DEFAULT_WORKSPACE_ID,
        "counts": {
            "memories": len(memories),
            "reminders": len(reminders),
        },
        "memories": [
            {
                "id": m.id,
                "type": m.type,
                "label": m.label,
                "content": m.content_ciphertext or "",
                "sensitivity": m.sensitivity,
                "provenance": m.provenance,
                "authority": m.authority,
                "confidence": m.confidence,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "updated_at": m.updated_at.isoformat() if m.updated_at else None,
            }
            for m in memories
        ],
        "reminders": [
            {
                "id": r.id,
                "title": r.title,
                "timezone": r.timezone,
                "recurrence_frequency": r.recurrence_frequency,
                "recurrence_interval": r.recurrence_interval,
                "priority": r.priority,
                "channel": r.channel,
                "status": r.status,
                "next_due_at": r.next_due_at.isoformat() if r.next_due_at else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reminders
        ],
    }

    # Compute checksum of plaintext (for integrity verification after import)
    plaintext_json = json.dumps(export_data_dict, default=str, sort_keys=True)
    checksum = hashlib.sha256(plaintext_json.encode("utf-8")).hexdigest()

    # Encrypt
    payload = encrypt_json(export_data_dict, req.passphrase)

    # Build final bundle
    bundle = {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "encrypted": True,
        "encryption": {
            "algorithm": "AES-256-GCM",
            "kdf": "PBKDF2-SHA256",
            "iterations": payload.iterations,
        },
        "checksum_sha256": checksum,
        "counts": export_data_dict["counts"],
        "data": payload.to_dict(),
    }

    return ExportResponse(
        bundle=bundle,
        checksum=checksum,
        memory_count=len(memories),
        reminder_count=len(reminders),
    )


@router.post("/import", response_model=ImportResponse)
async def import_data(
    req: ImportRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ImportResponse:
    """Import an encrypted JSON bundle, recreate memories + reminders.

    The passphrase must match the one used for export.
    Conflict policy determines how to handle duplicates (by original ID):
    - 'skip': keep existing, skip imported
    - 'overwrite': replace existing with imported
    - 'duplicate': create new with new ID
    """
    bundle = req.bundle

    # Validate bundle structure
    if not bundle.get("encrypted") or "data" not in bundle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid bundle: missing 'encrypted' or 'data' field",
        )

    # Decrypt
    try:
        payload = EncryptedPayload.from_dict(bundle["data"])
        data = decrypt_json(payload, req.passphrase)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decryption failed (wrong passphrase or corrupted data): {type(e).__name__}",
        ) from e

    # Verify checksum
    expected_checksum = bundle.get("checksum_sha256")
    if expected_checksum:
        plaintext_json = json.dumps(data, default=str, sort_keys=True)
        actual_checksum = hashlib.sha256(plaintext_json.encode("utf-8")).hexdigest()
        if actual_checksum != expected_checksum:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Checksum mismatch — data may be corrupted",
            )

    # Import memories
    memories_imported = 0
    memories_skipped = 0
    for mem_data in data.get("memories", []):
        existing = await db.get(MemoryNode, mem_data["id"])
        if existing is not None:
            if req.conflict_policy == "skip":
                memories_skipped += 1
                continue
            elif req.conflict_policy == "overwrite":
                existing.label = mem_data["label"]
                existing.content_ciphertext = mem_data.get("content", "")
                existing.type = mem_data["type"]
                existing.sensitivity = mem_data["sensitivity"]
                existing.version += 1
                memories_imported += 1
                continue
            elif req.conflict_policy == "duplicate":
                # Create with new ID
                mem_data = {**mem_data, "id": str(uuid4())}

        # Create new memory
        node = MemoryNode(
            id=mem_data["id"],
            workspace_id=DEFAULT_WORKSPACE_ID,
            type=mem_data["type"],
            label=mem_data["label"],
            content_ciphertext=mem_data.get("content", ""),
            content_format="text",
            source_type="imported_data",
            provenance="imported_data",
            authority="explicit",
            confidence=float(mem_data.get("confidence", 1.0)),
            sensitivity=mem_data["sensitivity"],
            status="active",
        )
        db.add(node)
        memories_imported += 1

    # Import reminders
    reminders_imported = 0
    reminders_skipped = 0
    for rem_data in data.get("reminders", []):
        existing = await db.get(Reminder, rem_data["id"])
        if existing is not None:
            if req.conflict_policy == "skip":
                reminders_skipped += 1
                continue
            elif req.conflict_policy == "duplicate":
                rem_data = {**rem_data, "id": str(uuid4())}

        # Parse datetime fields
        next_due_at = None
        if rem_data.get("next_due_at"):
            try:
                next_due_at = datetime.fromisoformat(rem_data["next_due_at"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        created_at = None
        if rem_data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(rem_data["created_at"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        reminder = Reminder(
            id=rem_data["id"],
            workspace_id=DEFAULT_WORKSPACE_ID,
            created_by_user_id="00000000-0000-0000-0000-000000000001",
            title=rem_data["title"],
            timezone=rem_data.get("timezone", "UTC"),
            recurrence_frequency=rem_data.get("recurrence_frequency", "none"),
            recurrence_interval=rem_data.get("recurrence_interval", 1),
            priority=rem_data.get("priority", "normal"),
            channel=rem_data.get("channel", "mock"),
            status=rem_data.get("status", "active"),
            next_due_at=next_due_at,
            created_at=created_at or datetime.now(timezone.utc),
            provenance="imported_data",
            authority="explicit",
            sensitivity="personal",
        )
        db.add(reminder)
        reminders_imported += 1

    await db.flush()

    return ImportResponse(
        memories_imported=memories_imported,
        memories_skipped=memories_skipped,
        reminders_imported=reminders_imported,
        reminders_skipped=reminders_skipped,
        checksum_verified=bool(expected_checksum),
    )
