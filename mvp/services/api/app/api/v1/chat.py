"""VNBOT API — Chat endpoints.

POST /chat — parse user input heuristically, return operation proposal.
POST /chat/operations/{id}/confirm — confirm a proposed operation, execute it.

Heuristic fallback per ADR-0007: this works WITHOUT LLM. LLM Router is added in 0.4.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vnbot_domain.entities.common import OperationStatus, RiskTier
from vnbot_domain.entities.reminders import (
    RecurrenceFrequency,
    Reminder,
    ReminderChannel,
    ReminderPriority,
    ReminderStatus,
)
from vnbot_domain.heuristics import Intent, ParseFailure, ParseSuccess, parse as heuristic_parse
from ...infrastructure.db.models import Operation as OperationModel
from ...infrastructure.db.models import Reminder as ReminderModel
from ...infrastructure.db.models import User, Workspace
from ...infrastructure.db.session import get_db
from ...schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConfirmRequest,
    ConfirmResponse,
    ProposalMemory,
    ProposalReminder,
)
from ...dependencies import get_workspace_id

router = APIRouter(tags=["chat"])

# Proposal TTL — late confirmations must re-validate
PROPOSAL_TTL_SECONDS = 300  # 5 minutes

# Default user + workspace IDs (single-user local mode for Phase 0.1)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"


async def _ensure_default_workspace(db: AsyncSession) -> str:
    """Ensure the default user + workspace exist. Idempotent."""
    user = await db.get(User, DEFAULT_USER_ID)
    if user is None:
        user = User(
            id=DEFAULT_USER_ID,
            email=None,
            display_name="Local User",
            status="active",
            timezone="America/Caracas",
            locale="es",
        )
        db.add(user)
        await db.flush()

    ws = await db.get(Workspace, DEFAULT_WORKSPACE_ID)
    if ws is None:
        ws = Workspace(
            id=DEFAULT_WORKSPACE_ID,
            owner_user_id=DEFAULT_USER_ID,
            name="Personal",
            type="personal",
            default_timezone="America/Caracas",
            settings_json={},
        )
        db.add(ws)
        await db.flush()

    return DEFAULT_WORKSPACE_ID


@router.post("/chat", response_model=ChatResponse)
async def post_chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ChatResponse:
    """Parse user input and return a proposal operation.

    Heuristic parse (no LLM). If parse fails, returns suggestion to configure LLM.
    """
    # Ensure workspace exists
    ws_id = await _ensure_default_workspace(db)
    operation_id = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=PROPOSAL_TTL_SECONDS)

    # Run heuristic parser
    result = heuristic_parse(req.text, tz_name=req.timezone)

    if isinstance(result, ParseFailure):
        # Store the failed operation for audit
        op = OperationModel(
            id=operation_id,
            workspace_id=ws_id,
            user_id=DEFAULT_USER_ID,
            agent_id="heuristic",
            conversation_id=req.conversation_id,
            type="chat_parse",
            status=OperationStatus.NEEDS_CLARIFICATION,
            risk_level=RiskTier.LOW,
            input_ref=_hash_input(req.text),
            proposal_json={
                "intent": result.intent.value,
                "raw_text": result.raw_text,
                "reason": result.reason,
            },
            requires_confirmation=False,
            expires_at=expires_at,
            idempotency_key=req.idempotency_key,
        )
        db.add(op)
        await db.flush()

        return ChatResponse(
            operation_id=operation_id,
            intent=result.intent.value,
            parsed=False,
            confidence=0.0,
            requires_confirmation=False,
            expires_at=expires_at,
            error=result.reason,
            suggestion=result.suggestion,
        )

    # ParseSuccess — build proposal
    assert isinstance(result, ParseSuccess)

    proposal_reminder: ProposalReminder | None = None
    proposal_memory: ProposalMemory | None = None
    op_type = "create_reminder"
    risk = RiskTier.LOW

    if result.reminder is not None:
        r = result.reminder
        proposal_reminder = ProposalReminder(
            title=r.title,
            due_at=r.due_at,
            timezone=r.timezone,
            recurrence_frequency=r.recurrence.frequency.value,
            recurrence_interval=r.recurrence.interval,
            priority=r.priority.value,
            channel=r.channel.value,
            confidence=r.confidence,
        )
        op_type = "create_reminder"
        risk = RiskTier.LOW
    elif result.memory is not None:
        m = result.memory
        proposal_memory = ProposalMemory(
            content=m.content,
            memory_type=m.memory_type,
            tags=m.tags,
            confidence=m.confidence,
        )
        op_type = "create_memory"
        risk = RiskTier.LOW

    # Store the proposal operation
    op = OperationModel(
        id=operation_id,
        workspace_id=ws_id,
        user_id=DEFAULT_USER_ID,
        agent_id="heuristic",
        conversation_id=req.conversation_id,
        type=op_type,
        status=OperationStatus.PROPOSED,
        risk_level=risk,
        input_ref=_hash_input(req.text),
        proposal_json={
            "intent": result.intent.value,
            "raw_text": result.raw_text,
            "reminder": proposal_reminder.model_dump(mode="json") if proposal_reminder else None,
            "memory": proposal_memory.model_dump(mode="json") if proposal_memory else None,
            "notes": result.notes,
        },
        requires_confirmation=True,
        expires_at=expires_at,
        idempotency_key=req.idempotency_key,
    )
    db.add(op)
    await db.flush()

    return ChatResponse(
        operation_id=operation_id,
        intent=result.intent.value,
        parsed=True,
        confidence=result.confidence,
        proposal_reminder=proposal_reminder,
        proposal_memory=proposal_memory,
        requires_confirmation=True,
        expires_at=expires_at,
        notes=result.notes,
    )


@router.post("/chat/operations/{operation_id}/confirm", response_model=ConfirmResponse)
async def confirm_operation(
    operation_id: str,
    req: ConfirmRequest,
    db: AsyncSession = Depends(get_db),
    workspace_id: str = Depends(get_workspace_id),
) -> ConfirmResponse:
    """Confirm a proposed operation and execute it.

    Re-validates the proposal (TTL check) before executing.
    Applies optional edits if provided.
    """
    # Ensure workspace exists (idempotent)
    await _ensure_default_workspace(db)

    # Load the operation
    op = await db.get(OperationModel, operation_id)
    if op is None or False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operation {operation_id} not found",
        )

    if op.status != OperationStatus.PROPOSED:
        return ConfirmResponse(
            operation_id=operation_id,
            status=op.status.value,
            error=f"Operation is in status {op.status.value}, cannot confirm",
        )

    # Check TTL — expired proposals need re-validation
    # SQLite stores datetimes as naive — coerce both sides to aware UTC for comparison
    if op.expires_at is not None:
        expires = op.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires:
            op.status = OperationStatus.EXPIRED
            await db.flush()
            return ConfirmResponse(
                operation_id=operation_id,
                status="expired",
                error="Proposal expired, please re-submit",
            )

    # Mark as confirmed + execute
    op.status = OperationStatus.EXECUTING
    op.confirmed_at = datetime.now(timezone.utc)
    await db.flush()

    try:
        # Execute based on operation type
        proposal = op.proposal_json
        entity_id: str | None = None
        entity_type: str | None = None
        next_due_at: datetime | None = None

        if op.type == "create_reminder" and proposal.get("reminder"):
            rem_data = proposal["reminder"]
            # Apply optional edits
            if req.edits:
                rem_data = {**rem_data, **req.edits}

            reminder = ReminderModel(
                id=str(uuid4()),
                workspace_id=op.workspace_id,
                created_by_user_id=op.user_id or DEFAULT_USER_ID,
                title=rem_data["title"],
                timezone=rem_data["timezone"],
                recurrence_frequency=RecurrenceFrequency(rem_data["recurrence_frequency"]),
                recurrence_interval=rem_data.get("recurrence_interval", 1),
                priority=ReminderPriority(rem_data.get("priority", "normal")),
                channel=ReminderChannel(rem_data.get("channel", "mock")),
                status=ReminderStatus.ACTIVE,
                next_due_at=datetime.fromisoformat(rem_data["due_at"].replace("Z", "+00:00"))
                if isinstance(rem_data["due_at"], str)
                else rem_data["due_at"],
                provenance="explicit_user_input",
                authority="user_confirmed",
                sensitivity="personal",
            )
            db.add(reminder)
            await db.flush()
            entity_id = reminder.id
            entity_type = "reminder"
            next_due_at = reminder.next_due_at

        elif op.type == "create_memory" and proposal.get("memory"):
            # Memory creation deferred to memories.py endpoint in 0.1 — placeholder
            entity_id = None
            entity_type = "memory"

        # Mark operation as succeeded
        op.status = OperationStatus.SUCCEEDED
        await db.flush()

        return ConfirmResponse(
            operation_id=operation_id,
            status="succeeded",
            entity_id=entity_id,
            entity_type=entity_type,
            next_due_at=next_due_at,
        )

    except Exception as e:
        op.status = OperationStatus.FAILED
        await db.flush()
        return ConfirmResponse(
            operation_id=operation_id,
            status="failed",
            error=str(e),
        )


def _hash_input(text: str) -> str:
    """SHA-256 hash of input — for audit log without storing plaintext."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
