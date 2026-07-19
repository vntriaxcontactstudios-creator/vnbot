"""VNBOT API — Local scheduler using APScheduler.

Computes which reminder occurrences to enqueue, generates them with idempotency,
and dispatches delivery jobs.

Per docs/03-ESQUEMA-BACKEND-VNBOT.md §14:
- Reminder ≠ occurrence. Recurring reminders are RULES, not duplicated rows.
- Scheduler tick: (1) find active reminders → (2) compute occurrences by timezone
  → (3) acquire lock → (4) enqueue idempotent job → (5) release lock.
- Occurrence key is deterministic: {reminder_id}:{due_at_utc}:{rule_version}
  → guarantees idempotent delivery.

In Phase 0.1 we use a single-process scheduler (AsyncIOScheduler). In Phase 0.3
this becomes a distributed scheduler with Redis locks.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import get_settings
from ..db.models import Notification, Reminder, ReminderOccurrence
from ..db.session import async_session_factory
from ..notifications.channels import (
    DeliveryResult,
    DeliveryStatus,
    get_channel,
    register_default_channels,
)
from vnbot_domain.entities.reminders import OccurrenceStatus, ReminderStatus

logger = logging.getLogger("vnbot.api.scheduler")

# Lookahead window — pre-generate occurrences up to N days ahead
LOOKAHEAD_DAYS = 30

# Tick interval — how often to scan for upcoming reminders
TICK_SECONDS = 60


class SchedulerService:
    """Manages reminder occurrence generation + delivery dispatch.

    Single-instance for Phase 0.1. For Phase 0.3+ (distributed), wrap with
    Redis-based locks to prevent duplicate occurrence generation across replicas.
    """

    def __init__(self) -> None:
        self._scheduler: AsyncIOScheduler | None = None
        self._started = False

    async def start(self) -> None:
        """Start the scheduler. Idempotent."""
        if self._started:
            return

        settings = get_settings()

        # Register default notification channels
        register_default_channels()

        # Create APScheduler with in-memory jobstore (jobs are our own logic,
        # not user-facing tasks). For persistence across restarts in 0.3+,
        # switch to SQLAlchemyJobStore.
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._scheduler.add_job(
            self.tick_generate_occurrences,
            trigger=IntervalTrigger(seconds=settings.scheduler_tick_seconds),
            id="generate_occurrences",
            replace_existing=True,
            max_instances=1,  # prevent overlapping ticks
            coalesce=True,
        )
        self._scheduler.add_job(
            self.tick_deliver_pending,
            trigger=IntervalTrigger(seconds=settings.scheduler_tick_seconds),
            id="deliver_pending",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        self._scheduler.start()
        self._started = True
        logger.info(
            f"Scheduler started (tick={settings.scheduler_tick_seconds}s, "
            f"lookahead={settings.scheduler_lookahead_days}d)"
        )

    async def stop(self) -> None:
        """Stop the scheduler. Idempotent."""
        if not self._started:
            return
        if self._scheduler:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
        self._started = False
        logger.info("Scheduler stopped")

    # ──────────────────────────────────────────────────────────────────────
    # Tick 1: generate occurrences for upcoming reminders
    # ──────────────────────────────────────────────────────────────────────

    async def tick_generate_occurrences(self) -> int:
        """Scan active reminders and generate occurrences within lookahead window.

        Returns the number of new occurrences generated.
        """
        if not self._started:
            return 0

        now = datetime.now(timezone.utc)
        lookahead_end = now + timedelta(days=LOOKAHEAD_DAYS)
        # SQLite stores datetimes as naive — use naive for the query filter
        lookahead_end_naive = lookahead_end.replace(tzinfo=None)
        generated = 0

        async with async_session_factory() as session:
            # Find all active reminders with next_due_at within lookahead window
            stmt = select(Reminder).where(
                Reminder.status == ReminderStatus.ACTIVE.value,
                Reminder.next_due_at.is_not(None),
                Reminder.next_due_at <= lookahead_end_naive,
            )
            result = await session.execute(stmt)
            reminders = result.scalars().all()

            for reminder in reminders:
                # Coerce next_due_at to aware UTC (SQLite stores naive)
                next_due = reminder.next_due_at
                if next_due is not None and next_due.tzinfo is None:
                    next_due = next_due.replace(tzinfo=timezone.utc)
                    reminder.next_due_at = next_due  # update in DB too

                # Generate occurrences from reminder.next_due_at up to lookahead_end
                occurrences = self._generate_occurrences_for(reminder, now, lookahead_end)
                for occ_data in occurrences:
                    # Check if occurrence already exists (idempotent)
                    existing = await session.execute(
                        select(ReminderOccurrence).where(
                            ReminderOccurrence.occurrence_key == occ_data["occurrence_key"]
                        )
                    )
                    if existing.scalar_one_or_none() is not None:
                        continue  # already generated, skip

                    # Create new occurrence
                    occ = ReminderOccurrence(
                        id=str(uuid4()),
                        reminder_id=reminder.id,
                        workspace_id=reminder.workspace_id,
                        occurrence_key=occ_data["occurrence_key"],
                        due_at=occ_data["due_at"],
                        timezone=reminder.timezone,
                        status=OccurrenceStatus.PENDING.value,
                    )
                    session.add(occ)
                    generated += 1

                    # Advance reminder.next_due_at if this is the latest occurrence
                    if next_due is not None and occ_data["due_at"] > next_due:
                        reminder.next_due_at = occ_data["next_after"]

            await session.commit()

        if generated:
            logger.info(f"Generated {generated} new reminder occurrences")
        return generated

    def _generate_occurrences_for(
        self, reminder: Reminder, now: datetime, lookahead_end: datetime
    ) -> list[dict]:
        """Compute occurrences for a reminder within the lookahead window.

        For one-off reminders: single occurrence at next_due_at (always generate,
        even if past — delivery worker handles past-due occurrences).
        For recurring reminders: compute next occurrences up to lookahead_end.
        """
        if reminder.next_due_at is None:
            return []

        occurrences: list[dict] = []
        due = reminder.next_due_at
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)

        # Always generate the next_due_at occurrence (even if past — delivery handles it)
        occ_key = self._make_occurrence_key(reminder.id, due, reminder.recurrence_rule_version)
        occurrences.append({
            "occurrence_key": occ_key,
            "due_at": due,
            "next_after": due,
        })

        # For recurring reminders, generate future occurrences up to lookahead_end
        if reminder.recurrence_frequency != "none":
            next_due = due
            while True:
                next_due = self._compute_next_occurrence(reminder, next_due)
                if next_due is None or next_due > lookahead_end:
                    break
                occ_key = self._make_occurrence_key(
                    reminder.id, next_due, reminder.recurrence_rule_version
                )
                occurrences.append({
                    "occurrence_key": occ_key,
                    "due_at": next_due,
                    "next_after": next_due,
                })

        return occurrences

    def _compute_next_occurrence(self, reminder: Reminder, after: datetime) -> datetime | None:
        """Compute the next occurrence strictly after the given time."""
        if after.tzinfo is None:
            after = after.replace(tzinfo=timezone.utc)

        interval = reminder.recurrence_interval or 1

        if reminder.recurrence_frequency == "daily":
            next_time = after + timedelta(days=interval)
        elif reminder.recurrence_frequency == "weekly":
            next_time = after + timedelta(weeks=interval)
        elif reminder.recurrence_frequency == "monthly":
            next_time = after + timedelta(days=30 * interval)
        elif reminder.recurrence_frequency == "yearly":
            try:
                next_time = after.replace(year=after.year + interval)
            except ValueError:  # Feb 29
                next_time = after.replace(year=after.year + interval, day=28)
        else:
            return None

        # Check recurrence_until
        if reminder.recurrence_until:
            until = reminder.recurrence_until
            if until.tzinfo is None:
                until = until.replace(tzinfo=timezone.utc)
            if next_time > until:
                return None

        return next_time

    def _make_occurrence_key(self, reminder_id: str, due_at: datetime, rule_version: int) -> str:
        """Compute deterministic occurrence_key.

        Format: {reminder_id}:{due_at_utc_iso}:v{rule_version}

        This is the idempotency guarantee: same reminder + same time + same rule
        always produces the same key, so duplicate scheduler ticks don't create
        duplicate occurrences.
        """
        due_iso = due_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{reminder_id}:{due_iso}:v{rule_version}"

    # ──────────────────────────────────────────────────────────────────────
    # Tick 2: deliver pending occurrences whose due_at has arrived
    # ──────────────────────────────────────────────────────────────────────

    async def tick_deliver_pending(self) -> int:
        """Find pending occurrences past their due_at and deliver them.

        Returns the number of delivery attempts made.
        """
        if not self._started:
            return 0

        now = datetime.now(timezone.utc)
        delivered = 0

        async with async_session_factory() as session:
            # Find pending occurrences past due_at
            # Note: SQLite stores datetimes as naive, so we compare with naive now
            now_naive = now.replace(tzinfo=None)
            stmt = select(ReminderOccurrence).where(
                ReminderOccurrence.status == OccurrenceStatus.PENDING.value,
                ReminderOccurrence.due_at <= now_naive,
            )
            result = await session.execute(stmt)
            pending = result.scalars().all()

            for occ in pending:
                # Mark as sending
                occ.status = OccurrenceStatus.SENDING.value
                occ.attempts += 1
                await session.flush()

                # Look up the reminder to get title + channel
                reminder = await session.get(Reminder, occ.reminder_id)
                if reminder is None:
                    occ.status = OccurrenceStatus.FAILED.value
                    occ.last_error_code = "reminder_not_found"
                    continue

                # Skip if reminder is no longer active (cancelled/completed)
                if reminder.status != ReminderStatus.ACTIVE.value:
                    occ.status = OccurrenceStatus.CANCELLED.value
                    logger.info(
                        f"Occurrence {occ.id} cancelled (reminder status={reminder.status})"
                    )
                    continue

                # Create + send notification
                notification = Notification(
                    id=str(uuid4()),
                    workspace_id=occ.workspace_id,
                    occurrence_id=occ.id,
                    channel=reminder.channel,
                    title=reminder.title,
                    body_ciphertext=reminder.description_ciphertext,
                    status="pending",
                    priority=reminder.priority,
                )
                session.add(notification)
                await session.flush()

                # Look up channel implementation
                channel_impl = get_channel(reminder.channel)
                if channel_impl is None:
                    occ.status = OccurrenceStatus.FAILED.value
                    occ.last_error_code = f"channel_not_registered:{reminder.channel}"
                    notification.status = "failed"
                    logger.error(
                        f"Channel '{reminder.channel}' not registered for occurrence {occ.id}"
                    )
                    continue

                # Deliver
                delivery = await channel_impl.send(notification)

                if delivery.status == DeliveryStatus.DELIVERED:
                    occ.status = OccurrenceStatus.DELIVERED.value
                    occ.delivered_at = datetime.now(timezone.utc)
                    notification.status = "delivered"
                    delivered += 1
                    logger.info(
                        f"Occurrence {occ.id} delivered via {reminder.channel}"
                    )

                    # For one-off reminders, mark reminder as completed
                    if reminder.recurrence_frequency == "none":
                        reminder.status = ReminderStatus.COMPLETED.value
                        reminder.completed_at = datetime.now(timezone.utc)
                elif delivery.status == DeliveryStatus.SKIPPED:
                    occ.status = OccurrenceStatus.DELIVERED.value
                    notification.status = "delivered"
                    logger.info(f"Occurrence {occ.id} skipped (already delivered)")
                else:
                    occ.status = OccurrenceStatus.FAILED.value
                    occ.last_error_code = delivery.error_code
                    notification.status = "failed"
                    logger.error(
                        f"Occurrence {occ.id} delivery failed: {delivery.error_message}"
                    )

            await session.commit()

        if delivered:
            logger.info(f"Delivered {delivered} pending occurrences")
        return delivered

    # ──────────────────────────────────────────────────────────────────────
    # Manual trigger (for testing)
    # ──────────────────────────────────────────────────────────────────────

    async def trigger_now(self) -> dict[str, int]:
        """Trigger both ticks immediately. For testing/dev."""
        generated = await self.tick_generate_occurrences()
        delivered = await self.tick_deliver_pending()
        return {"generated": generated, "delivered": delivered}


# Singleton
scheduler_service = SchedulerService()
