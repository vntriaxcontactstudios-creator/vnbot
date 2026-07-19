"""VNBOT API — Export/Import schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    """POST /export — request to export all data as encrypted bundle."""

    passphrase: str = Field(..., min_length=8, max_length=500, description="Encryption passphrase")


class ExportResponse(BaseModel):
    """Response with encrypted bundle."""

    bundle: dict[str, Any] = Field(..., description="Encrypted JSON bundle (self-contained)")
    checksum: str = Field(..., description="SHA-256 checksum of plaintext (for verification)")
    memory_count: int
    reminder_count: int


class ImportRequest(BaseModel):
    """POST /import — import an encrypted bundle."""

    bundle: dict[str, Any] = Field(..., description="Encrypted bundle from /export")
    passphrase: str = Field(..., min_length=8, max_length=500, description="Same passphrase used for export")
    conflict_policy: Literal["skip", "overwrite", "duplicate"] = Field(
        default="skip",
        description="How to handle items with existing IDs",
    )


class ImportResponse(BaseModel):
    """Response with import results."""

    memories_imported: int
    memories_skipped: int
    reminders_imported: int
    reminders_skipped: int
    checksum_verified: bool
