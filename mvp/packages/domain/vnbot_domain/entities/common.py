"""VNBOT Domain — Common types and enums.

Pure Python dataclasses + enums. NO ORM, NO Pydantic models here (those are
in the schemas/ layer). This module is the source of truth for domain types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


# ──────────────────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────────────────


class Provenance(str, Enum):
    """Where a piece of data came from (per docs/07 §2.2)."""

    EXPLICIT_USER_INPUT = "explicit_user_input"
    USER_CONFIRMED = "user_confirmed"
    CONVERSATION_EXTRACTION = "conversation_extraction"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    IMAGE_OCR = "image_ocr"
    LLM_INFERENCE = "llm_inference"
    EXTERNAL_INTEGRATION = "external_integration"
    IMPORTED_DATA = "imported_data"
    SYSTEM_GENERATED = "system_generated"


class Authority(str, Enum):
    """How authoritative a piece of data is (per docs/07 §9)."""

    EXPLICIT = "explicit"
    USER_CONFIRMED = "user_confirmed"
    SYSTEM_EXTRACTED = "system_extracted"
    INFERRED = "inferred"
    EXTERNAL_SOURCE = "external_source"


class Sensitivity(str, Enum):
    """Data sensitivity level (per docs/07 §9)."""

    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    SECRET = "secret"


class AutonomyLevel(int, Enum):
    """Agent autonomy levels (per docs/09 §16). 0=most restrictive, 4=most permissive."""

    ANSWER_ONLY = 0
    PROPOSE = 1
    INTERNAL_ACTIONS = 2
    EXTERNAL_CONFIRMED = 3
    BOUNDED_AUTOMATION = 4


class RiskTier(str, Enum):
    """Risk tier of an operation (per docs/06 §27)."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"  # not in MVP


class OperationStatus(str, Enum):
    """Operation lifecycle (per docs/03 §7.2)."""

    RECEIVED = "received"
    CLASSIFYING = "classifying"
    PROPOSED = "proposed"
    NEEDS_CLARIFICATION = "needs_clarification"
    WAITING_CONFIRMATION = "waiting_confirmation"
    QUEUED = "queued"
    EXECUTING = "executing"
    RETRYING = "retrying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class JobStatus(str, Enum):
    """Async job status (per docs/03 §15.1)."""

    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEAD_LETTER = "dead_letter"


class JobPriority(str, Enum):
    """Job priority levels (per docs/03 §15.1)."""

    CRITICAL = "critical"  # security/restore
    HIGH = "high"  # near reminders
    NORMAL = "normal"  # transcription/embeddings
    LOW = "low"  # consolidation/stats


# ──────────────────────────────────────────────────────────────────────────────
# Base value object
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ValueObject:
    """Base for value objects (immutable, compared by value)."""


@dataclass(frozen=True)
class EntityId(ValueObject):
    """Strongly-typed entity ID. Wraps UUID v4."""

    value: UUID

    @classmethod
    def generate(cls) -> EntityId:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, s: str) -> EntityId:
        return cls(UUID(s))


# ──────────────────────────────────────────────────────────────────────────────
# Timestamps
# ──────────────────────────────────────────────────────────────────────────────


def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class TimeRange(ValueObject):
    """Inclusive time range [start, end]."""

    start: datetime
    end: datetime

    def contains(self, t: datetime) -> bool:
        return self.start <= t <= self.end

    def duration_seconds(self) -> float:
        return (self.end - self.start).total_seconds()


# ──────────────────────────────────────────────────────────────────────────────
# Operation (cross-cutting)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class Operation:
    """Lifecycle record of every user/agent-initiated action (per docs/03 §7.2).

    Every mutating command must create an Operation. The idempotency_key
    allows safe retries: same key → same result.
    """

    id: UUID
    workspace_id: UUID
    user_id: UUID | None
    agent_id: str | None
    conversation_id: UUID | None
    type: str
    status: OperationStatus
    risk_level: RiskTier
    input_ref: str | None = None
    proposal_json: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    confirmed_at: datetime | None = None
    expires_at: datetime | None = None
    idempotency_key: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
