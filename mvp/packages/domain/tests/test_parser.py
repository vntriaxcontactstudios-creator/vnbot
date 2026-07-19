"""VNBOT Domain — Heuristic parser tests.

Validates 20+ input cases per PRD §18 requirement.
Run: pytest packages/domain/tests/test_parser.py -v
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from zoneinfo import ZoneInfo

from vnbot_domain.heuristics import (
    Intent,
    ParseSuccess,
    parse,
)
from vnbot_domain.entities.reminders import RecurrenceFrequency


# Fixtures
TZ_CARACAS = "America/Caracas"
NOW_MONDAY_10AM = datetime(2026, 7, 20, 14, 0, 0, tzinfo=timezone.utc)  # Monday 10am Caracas


# ──────────────────────────────────────────────────────────────────────────────
# Intent detection (8 cases)
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_intent_recuerdame():
    result = parse("Recuérdame mañana a las 9 revisar VNBOT", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.intent == Intent.CREATE_REMINDER


@pytest.mark.unit
def test_intent_avisame():
    result = parse("Avísame el viernes a las 3 de la tarde llamar a mamá", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.intent == Intent.CREATE_REMINDER


@pytest.mark.unit
def test_intent_tengo_que():
    result = parse("Tengo que enviar el reporte mañana", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.intent == Intent.CREATE_TASK


@pytest.mark.unit
def test_intent_necesito():
    result = parse("Necesito comprar leche pasado mañana", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.intent == Intent.CREATE_TASK


@pytest.mark.unit
def test_intent_guarda_que():
    result = parse("Guarda que el cumpleaños de Daniel es el 15 de agosto", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.intent == Intent.CREATE_MEMORY


@pytest.mark.unit
def test_intent_anota():
    result = parse("Anota: la contraseña del wifi es vnbot123", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.intent == Intent.CREATE_MEMORY


@pytest.mark.unit
def test_intent_anade_a_la_lista():
    result = parse("Añade a la lista: pan, leche, huevos", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.intent == Intent.CREATE_LIST_ITEM


@pytest.mark.unit
def test_intent_unknown():
    from vnbot_domain.heuristics import ParseFailure

    result = parse("Hola, ¿cómo estás?", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseFailure)
    assert result.intent == Intent.UNKNOWN


# ──────────────────────────────────────────────────────────────────────────────
# Date parsing (6 cases)
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_date_manana():
    result = parse("Recuérdame mañana a las 9 revisar VNBOT", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    # Tomorrow in Caracas timezone
    tz = ZoneInfo(TZ_CARACAS)
    expected = (NOW_MONDAY_10AM + __import__("datetime").timedelta(days=1)).astimezone(tz)
    expected = expected.replace(hour=9, minute=0, second=0, microsecond=0)
    assert result.reminder.due_at == expected


@pytest.mark.unit
def test_date_pasado_manana():
    from datetime import timedelta

    result = parse("Recuérdame pasado mañana a las 10 llamar al banco", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    tz = ZoneInfo(TZ_CARACAS)
    expected = (NOW_MONDAY_10AM + timedelta(days=2)).astimezone(tz)
    expected = expected.replace(hour=10, minute=0, second=0, microsecond=0)
    assert result.reminder.due_at == expected


@pytest.mark.unit
def test_date_weekday_lunes():
    result = parse("Recuérdame el lunes a las 9 empezar la dieta", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    # "lunes" when today is Monday → next Monday (7 days)
    tz = ZoneInfo(TZ_CARACAS)
    expected = (NOW_MONDAY_10AM + __import__("datetime").timedelta(days=7)).astimezone(tz)
    expected = expected.replace(hour=9, minute=0, second=0, microsecond=0)
    assert result.reminder.due_at == expected


@pytest.mark.unit
def test_date_proximo_viernes():
    from datetime import timedelta

    result = parse("Avísame el próximo viernes a las 5 reunión equipo", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    # Friday is 4 days after Monday → "próximo viernes" forces next week (11 days)
    # "a las 5" without qualifier → ambiguous, parser assumes evening (5pm = 17:00)
    tz = ZoneInfo(TZ_CARACAS)
    expected = (NOW_MONDAY_10AM + timedelta(days=11)).astimezone(tz)
    expected = expected.replace(hour=17, minute=0, second=0, microsecond=0)
    assert result.reminder.due_at == expected


@pytest.mark.unit
def test_date_en_3_dias():
    from datetime import timedelta

    result = parse("Recuérdame en 3 días a las 8 pagar la factura", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    tz = ZoneInfo(TZ_CARACAS)
    expected = (NOW_MONDAY_10AM + timedelta(days=3)).astimezone(tz)
    expected = expected.replace(hour=8, minute=0, second=0, microsecond=0)
    assert result.reminder.due_at == expected


@pytest.mark.unit
def test_date_hoy():
    result = parse("Recuérdame hoy a las 20 cerrar las ventanas", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    # "hoy" + "a las 20" → today at 20:00 (which is future since now is 10am)
    tz = ZoneInfo(TZ_CARACAS)
    expected = NOW_MONDAY_10AM.astimezone(tz).replace(hour=20, minute=0, second=0, microsecond=0)
    assert result.reminder.due_at == expected


# ──────────────────────────────────────────────────────────────────────────────
# Time parsing (5 cases)
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_time_simple():
    result = parse("Recuérdame mañana a las 9 revisar VNBOT", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.due_at.hour == 9
    assert result.reminder.due_at.minute == 0


@pytest.mark.unit
def test_time_with_minutes():
    result = parse("Recuérdame mañana a las 9:30 reunión", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.due_at.hour == 9
    assert result.reminder.due_at.minute == 30


@pytest.mark.unit
def test_time_tarde():
    result = parse("Recuérdame mañana a las 3 de la tarde dentista", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.due_at.hour == 15  # 3pm = 15:00


@pytest.mark.unit
def test_time_noche():
    result = parse("Avísame mañana a las 9 de la noche apagar luces", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.due_at.hour == 21  # 9pm = 21:00


@pytest.mark.unit
def test_time_mediodia():
    result = parse("Recuérdame mañana al mediodía almorzar", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.due_at.hour == 12


# ──────────────────────────────────────────────────────────────────────────────
# Recurrence parsing (4 cases)
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_recurrence_daily():
    result = parse("Recuérdame cada día a las 8 tomar pastilla", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.recurrence.frequency == RecurrenceFrequency.DAILY
    assert result.reminder.recurrence.interval == 1


@pytest.mark.unit
def test_recurrence_weekly():
    result = parse("Recuérdame cada semana llamar a mi mamá", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.recurrence.frequency == RecurrenceFrequency.WEEKLY


@pytest.mark.unit
def test_recurrence_every_3_days():
    result = parse("Recuérdame cada 3 días revisar las plantas", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.recurrence.frequency == RecurrenceFrequency.DAILY
    assert result.reminder.recurrence.interval == 3


@pytest.mark.unit
def test_recurrence_monthly():
    result = parse("Recuérdame cada mes pagar el alquiler", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.recurrence.frequency == RecurrenceFrequency.MONTHLY


# ──────────────────────────────────────────────────────────────────────────────
# Title extraction (3 cases)
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_title_reminder():
    result = parse("Recuérdame mañana a las 9 revisar VNBOT", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.title == "Revisar VNBOT"


@pytest.mark.unit
def test_title_task():
    result = parse("Tengo que enviar el reporte mañana", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert "reporte" in result.reminder.title.lower()


@pytest.mark.unit
def test_title_memory():
    result = parse("Guarda que el cumpleaños de Daniel es el 15 de agosto", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.memory is not None
    assert "cumpleaños" in result.memory.content.lower()
    assert "Daniel" in result.memory.content


# ──────────────────────────────────────────────────────────────────────────────
# Edge cases (4 cases)
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_empty_input():
    from vnbot_domain.heuristics import ParseFailure

    result = parse("", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseFailure)
    assert "vacía" in result.reason.lower() or "empty" in result.reason.lower()


@pytest.mark.unit
def test_no_date_no_time():
    from vnbot_domain.heuristics import ParseFailure

    result = parse("Recuérdame algo", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseFailure)
    assert "fecha" in result.reason.lower() or "hora" in result.reason.lower()


@pytest.mark.unit
def test_past_date():
    from vnbot_domain.heuristics import ParseFailure

    # "hoy" + "a las 5" when now is 10am → time already passed today
    result = parse("Recuérdame hoy a las 5 cerrar las ventanas", TZ_CARACAS, NOW_MONDAY_10AM)
    # Heuristic should reschedule to tomorrow (or return failure)
    if isinstance(result, ParseSuccess):
        assert result.reminder is not None
        # Must be in the future
        assert result.reminder.due_at > NOW_MONDAY_10AM
    else:
        assert isinstance(result, ParseFailure)


@pytest.mark.unit
def test_memory_with_tags():
    result = parse("Guarda que el wifi es vnbot123 #casa #passwords", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.memory is not None
    assert "casa" in result.memory.tags
    assert "passwords" in result.memory.tags


# ──────────────────────────────────────────────────────────────────────────────
# Confidence levels (2 cases)
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_confidence_date_and_time():
    result = parse("Recuérdame mañana a las 9:30 reunión", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.confidence == 1.0  # both date + time


@pytest.mark.unit
def test_confidence_date_only():
    result = parse("Recuérdame mañana almorzar", TZ_CARACAS, NOW_MONDAY_10AM)
    assert isinstance(result, ParseSuccess)
    assert result.reminder is not None
    assert result.reminder.confidence == 0.7  # date only, default time
