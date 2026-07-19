"""VNBOT Domain — Reminder entity tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from zoneinfo import ZoneInfo

from vnbot_domain.entities import (
    OccurrenceStatus,
    RecurrenceFrequency,
    RecurrenceRule,
    Reminder,
    ReminderOccurrence,
    ReminderStatus,
)


@pytest.mark.unit
def test_reminder_create():
    """A reminder can be created with the minimum required fields."""
    now = datetime.now(timezone.utc)
    reminder = Reminder(
        id=uuid4(),
        workspace_id=uuid4(),
        created_by_user_id=uuid4(),
        title="Revisar VNBOT",
        next_due_at=now + timedelta(days=1),
    )
    assert reminder.status == ReminderStatus.ACTIVE
    assert reminder.priority.value == "normal"
    assert reminder.version == 1


@pytest.mark.unit
def test_reminder_empty_title_fails():
    """Empty title raises ValueError."""
    with pytest.raises(ValueError, match="title"):
        Reminder(
            id=uuid4(),
            workspace_id=uuid4(),
            created_by_user_id=uuid4(),
            title="",
        )


@pytest.mark.unit
def test_reminder_complete():
    reminder = Reminder(
        id=uuid4(),
        workspace_id=uuid4(),
        created_by_user_id=uuid4(),
        title="Test",
    )
    reminder.complete()
    assert reminder.status == ReminderStatus.COMPLETED
    assert reminder.completed_at is not None
    assert reminder.version == 2


@pytest.mark.unit
def test_reminder_cancel():
    reminder = Reminder(
        id=uuid4(),
        workspace_id=uuid4(),
        created_by_user_id=uuid4(),
        title="Test",
    )
    reminder.cancel()
    assert reminder.status == ReminderStatus.CANCELLED
    assert reminder.cancelled_at is not None


@pytest.mark.unit
def test_reminder_pause_resume():
    reminder = Reminder(
        id=uuid4(),
        workspace_id=uuid4(),
        created_by_user_id=uuid4(),
        title="Test",
    )
    reminder.pause()
    assert reminder.status == ReminderStatus.PAUSED
    reminder.resume()
    assert reminder.status == ReminderStatus.ACTIVE


@pytest.mark.unit
def test_reminder_snooze():
    reminder = Reminder(
        id=uuid4(),
        workspace_id=uuid4(),
        created_by_user_id=uuid4(),
        title="Test",
        next_due_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    new_time = datetime.now(timezone.utc) + timedelta(hours=3)
    reminder.snooze(new_time)
    assert reminder.next_due_at == new_time


@pytest.mark.unit
def test_reminder_snooze_past_fails():
    reminder = Reminder(
        id=uuid4(),
        workspace_id=uuid4(),
        created_by_user_id=uuid4(),
        title="Test",
    )
    with pytest.raises(ValueError, match="future"):
        reminder.snooze(datetime.now(timezone.utc) - timedelta(hours=1))


@pytest.mark.unit
def test_occurrence_key_deterministic():
    """Same reminder + same due_at + same rule_version = same key."""
    reminder_id = uuid4()
    due_at = datetime(2026, 7, 21, 9, 0, 0, tzinfo=timezone.utc)

    key1 = ReminderOccurrence.generate_key(reminder_id, due_at, rule_version=1)
    key2 = ReminderOccurrence.generate_key(reminder_id, due_at, rule_version=1)

    assert key1 == key2


@pytest.mark.unit
def test_occurrence_key_different_reminder():
    """Different reminder_id → different key."""
    due_at = datetime(2026, 7, 21, 9, 0, 0, tzinfo=timezone.utc)
    key1 = ReminderOccurrence.generate_key(uuid4(), due_at)
    key2 = ReminderOccurrence.generate_key(uuid4(), due_at)
    assert key1 != key2


@pytest.mark.unit
def test_occurrence_key_different_time():
    """Same reminder + different due_at → different key."""
    reminder_id = uuid4()
    key1 = ReminderOccurrence.generate_key(
        reminder_id, datetime(2026, 7, 21, 9, 0, 0, tzinfo=timezone.utc)
    )
    key2 = ReminderOccurrence.generate_key(
        reminder_id, datetime(2026, 7, 21, 10, 0, 0, tzinfo=timezone.utc)
    )
    assert key1 != key2


@pytest.mark.unit
def test_occurrence_mark_delivered():
    occ = ReminderOccurrence(
        id=uuid4(),
        reminder_id=uuid4(),
        workspace_id=uuid4(),
        occurrence_key="test-key",
        due_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    occ.mark_delivered()
    assert occ.status == OccurrenceStatus.DELIVERED
    assert occ.delivered_at is not None


@pytest.mark.unit
def test_occurrence_double_deliver_fails():
    occ = ReminderOccurrence(
        id=uuid4(),
        reminder_id=uuid4(),
        workspace_id=uuid4(),
        occurrence_key="test-key",
        due_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    occ.mark_delivered()
    with pytest.raises(ValueError, match="terminal"):
        occ.mark_delivered()


@pytest.mark.unit
def test_recurrence_rule_next_occurrence_daily():
    rule = RecurrenceRule(frequency=RecurrenceFrequency.DAILY, interval=1)
    now = datetime(2026, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
    next_occ = rule.next_occurrence_after(now)
    assert next_occ is not None
    assert next_occ.day == 21  # next day


@pytest.mark.unit
def test_recurrence_rule_none_returns_none():
    rule = RecurrenceRule(frequency=RecurrenceFrequency.NONE)
    now = datetime(2026, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
    assert rule.next_occurrence_after(now) is None


@pytest.mark.unit
def test_recurrence_rule_until_limits():
    """If until is in the past, no more occurrences."""
    rule = RecurrenceRule(
        frequency=RecurrenceFrequency.DAILY,
        until=datetime(2026, 7, 19, 0, 0, 0, tzinfo=timezone.utc),
    )
    now = datetime(2026, 7, 20, 10, 0, 0, tzinfo=timezone.utc)
    assert rule.next_occurrence_after(now) is None
