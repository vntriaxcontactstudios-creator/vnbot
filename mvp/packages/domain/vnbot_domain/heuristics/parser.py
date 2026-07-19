"""VNBOT Domain — Heuristic Parser (mandatory fallback before LLM).

Parses natural language input into structured operations WITHOUT calling an LLM.
This is the fallback chain endpoint: primary LLM → secondary LLM → local LLM → heuristics.

The parser must:
- Detect common intent keywords (Recuérdame, Avísame, Tengo que, etc.)
- Resolve relative dates ("mañana", "próximo lunes")
- Parse times ("a las 9", "a las 9:30", "a las 9 de la noche")
- Apply timezone
- Flag low confidence when unsure (caller decides whether to escalate to LLM)
- Never invent data — if cannot parse, return ParseFailure with helpful message

Per PRD §18, heuristics must NOT:
- Infer relations between memories
- Interpret images/audio
- Generate briefings
- Operate MCP tools
- Handle complex multi-turn context
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from zoneinfo import ZoneInfo

from ..entities.reminders import (
    RecurrenceFrequency,
    RecurrenceRule,
    ReminderChannel,
    ReminderPriority,
)


class Intent(str, Enum):
    """Detected user intent."""

    CREATE_REMINDER = "create_reminder"
    CREATE_MEMORY = "create_memory"
    CREATE_TASK = "create_task"
    CREATE_LIST_ITEM = "create_list_item"
    QUERY_MEMORIES = "query_memories"
    LIST_REMINDERS = "list_reminders"
    COMPLETE_REMINDER = "complete_reminder"
    DELETE_MEMORY = "delete_memory"
    UNKNOWN = "unknown"


@dataclass
class ParsedReminder:
    """Structured result of parsing a reminder intent."""

    title: str
    due_at: datetime
    timezone: str
    recurrence: RecurrenceRule = field(default_factory=RecurrenceRule)
    priority: ReminderPriority = ReminderPriority.NORMAL
    channel: ReminderChannel = ReminderChannel.MOCK
    confidence: float = 1.0


@dataclass
class ParsedMemory:
    """Structured result of parsing a memory intent."""

    content: str
    memory_type: str = "note"
    tags: list[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class ParseSuccess:
    """Successful parse result."""

    intent: Intent
    reminder: ParsedReminder | None = None
    memory: ParsedMemory | None = None
    raw_text: str = ""
    confidence: float = 1.0
    notes: list[str] = field(default_factory=list)


@dataclass
class ParseFailure:
    """Failed parse result. Caller should escalate to LLM."""

    intent: Intent
    raw_text: str
    reason: str
    suggestion: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# Intent detection patterns (per PRD §18 + Plan §6)
# ──────────────────────────────────────────────────────────────────────────────

INTENT_PATTERNS: dict[Intent, list[re.Pattern[str]]] = {
    Intent.CREATE_REMINDER: [
        re.compile(r"\b(recu[eé]rdame|av[ií]same|notif[ií]came|record[áa]me)\b", re.IGNORECASE),
        re.compile(r"\b(no me olvides|no olvides)\b", re.IGNORECASE),
    ],
    Intent.CREATE_TASK: [
        re.compile(r"\b(tengo que|necesito|debo|tengo pendiente)\b", re.IGNORECASE),
    ],
    Intent.CREATE_MEMORY: [
        re.compile(r"\b(guarda que|anota|memoriza|apunta que|registra que)\b", re.IGNORECASE),
        re.compile(r"\b(recuerda que|recuerda el dato)\b", re.IGNORECASE),
    ],
    Intent.CREATE_LIST_ITEM: [
        re.compile(r"\b(a[ñn]ade a la lista|agrega a la lista|pon en la lista)\b", re.IGNORECASE),
    ],
    Intent.QUERY_MEMORIES: [
        re.compile(r"\b(que recuerdas|qu[eé] recuerdas|que tengo guardado|qu[eé] tengo guardado)\b", re.IGNORECASE),
        re.compile(r"\b(busca (en mis )?memorias|busca (en mi )?memoria)\b", re.IGNORECASE),
    ],
    Intent.LIST_REMINDERS: [
        re.compile(r"\b(que recordatorios|qu[eé] recordatorios|mis recordatorios)\b", re.IGNORECASE),
        re.compile(r"\b(que tengo que hacer|qu[eé] tengo que hacer|mis pendientes)\b", re.IGNORECASE),
    ],
    Intent.COMPLETE_REMINDER: [
        re.compile(r"\b(ya (lo )?hice|ya (lo )?complet[eé]|marca como hecho)\b", re.IGNORECASE),
    ],
    Intent.DELETE_MEMORY: [
        re.compile(r"\b(olvida que|borra (el )?recuerdo|elimina (la )?memoria)\b", re.IGNORECASE),
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# Date and time parsing
# ──────────────────────────────────────────────────────────────────────────────


# Relative date keywords → offset in days from today
RELATIVE_DATES: dict[str, int] = {
    "hoy": 0,
    "mañana": 1,
    "manana": 1,
    "pasado mañana": 2,
    "pasado manana": 2,
}

# Weekday names (Spanish) → weekday number (0=Monday)
WEEKDAYS: dict[str, int] = {
    "lunes": 0,
    "martes": 1,
    "miércoles": 2,
    "miercoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sábado": 5,
    "sabado": 5,
    "domingo": 6,
}

# Time of day aliases → hour
TIME_ALIASES: dict[str, int] = {
    "mediodía": 12,
    "mediodia": 12,
    "medianoche": 0,
    "mañana": 9,  # default morning hour
    "manana": 9,
    "tarde": 15,
    "noche": 20,
}


def parse_relative_date(text: str, now: datetime, tz: ZoneInfo) -> datetime | None:
    """Parse a relative date expression from text.

    Returns the resolved datetime in the given timezone, or None if no date found.
    """
    text_lower = text.lower()

    # Check for "pasado mañana" first (2-word phrase)
    if "pasado mañana" in text_lower or "pasado manana" in text_lower:
        target = now + timedelta(days=2)
        return _make_datetime(target, tz)

    # Check simple relative dates
    for keyword, offset in RELATIVE_DATES.items():
        if offset == 2:
            continue  # already handled above
        if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
            target = now + timedelta(days=offset)
            return _make_datetime(target, tz)

    # Check weekdays
    for day_name, target_weekday in WEEKDAYS.items():
        if re.search(rf"\b{re.escape(day_name)}\b", text_lower):
            days_ahead = (target_weekday - now.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7  # next week, not today
            # "próximo" prefix forces next week
            if re.search(rf"\b(pr[oó]ximo|siguiente)\s+{re.escape(day_name)}\b", text_lower):
                days_ahead = ((target_weekday - now.weekday()) % 7) or 7
                if days_ahead <= 7:
                    days_ahead += 7
            target = now + timedelta(days=days_ahead)
            return _make_datetime(target, tz)

    # Check "en N días/semanas/meses"
    m = re.search(r"\ben\s+(\d+)\s+(d[ií]as?|semanas?|meses?|a[ñn]os?)\b", text_lower)
    if m:
        n = int(m.group(1))
        unit = m.group(2).rstrip("s")
        if unit.startswith("d"):
            target = now + timedelta(days=n)
        elif unit.startswith("semana"):
            target = now + timedelta(weeks=n)
        elif unit.startswith("mes"):
            target = now + timedelta(days=30 * n)
        else:  # año
            try:
                target = now.replace(year=now.year + n)
            except ValueError:  # Feb 29
                target = now.replace(year=now.year + n, day=28)
        return _make_datetime(target, tz)

    return None


def parse_time(text: str, default_hour: int = 9) -> tuple[int, int] | None:
    """Parse a time expression from text.

    Returns (hour, minute) in 24h format, or None if no time found.

    Note: "mañana" is ambiguous — it can mean "tomorrow" (date) or "morning" (time).
    We treat "mañana" as date by default (handled in parse_relative_date).
    Time alias "mañana" only triggers when explicitly preceded by "a la" or "en la".
    """
    text_lower = text.lower()

    # "a las 9", "a las 9:30", "a las 9 de la noche"
    m = re.search(r"\ba\s+las?\s+(\d{1,2})(?::(\d{2}))?\b", text_lower)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0

        # Check for "de la tarde/noche" suffix
        if re.search(r"\bde\s+la\s+(tarde|noche)\b", text_lower):
            if hour < 12:
                hour += 12
        elif re.search(r"\bde\s+la\s+mañana\b", text_lower):
            pass  # already morning
        elif re.search(r"\bpm\b", text_lower) or re.search(r"\bp\.m\.", text_lower):
            if hour < 12:
                hour += 12
        elif re.search(r"\bam\b", text_lower) or re.search(r"\ba\.m\.", text_lower):
            if hour == 12:
                hour = 0
        elif hour <= 6:
            # Ambiguous — assume evening (most reminders are for afternoon/evening)
            hour += 12

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return (hour, minute)

    # Check time aliases (mediodía, medianoche, tarde, noche)
    # SKIP "mañana" here — it's primarily a date keyword.
    # Only match "mañana" as time when explicit "a la mañana" or "en la mañana"
    for alias, alias_hour in TIME_ALIASES.items():
        if alias in ("mañana", "manana"):
            # Only match if preceded by "a la" or "en la"
            if re.search(rf"\b(a\s+la|en\s+la)\s+{re.escape(alias)}\b", text_lower):
                return (alias_hour, 0)
        else:
            if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                return (alias_hour, 0)

    return None


def _make_datetime(date: datetime, tz: ZoneInfo) -> datetime:
    """Combine a date with default time (9:00) in the given timezone."""
    localized = date.astimezone(tz)
    return localized.replace(hour=9, minute=0, second=0, microsecond=0)


# ──────────────────────────────────────────────────────────────────────────────
# Recurrence parsing
# ──────────────────────────────────────────────────────────────────────────────


def parse_recurrence(text: str) -> RecurrenceRule:
    """Detect recurrence pattern from text."""
    text_lower = text.lower()

    if re.search(r"\b(cada d[ií]a|diariamente|todos los d[ií]as)\b", text_lower):
        return RecurrenceRule(frequency=RecurrenceFrequency.DAILY, interval=1)

    if re.search(r"\b(cada\s+(\d+)\s+d[ií]as?)\b", text_lower):
        m = re.search(r"\bcada\s+(\d+)\s+d[ií]as?", text_lower)
        if m:
            return RecurrenceRule(frequency=RecurrenceFrequency.DAILY, interval=int(m.group(1)))

    if re.search(r"\b(cada semana|semanalmente|todas las semanas)\b", text_lower):
        return RecurrenceRule(frequency=RecurrenceFrequency.WEEKLY, interval=1)

    if re.search(r"\b(cada\s+(\d+)\s+semanas?)\b", text_lower):
        m = re.search(r"\bcada\s+(\d+)\s+semanas?", text_lower)
        if m:
            return RecurrenceRule(frequency=RecurrenceFrequency.WEEKLY, interval=int(m.group(1)))

    if re.search(r"\b(cada mes|mensualmente|todos los meses)\b", text_lower):
        return RecurrenceRule(frequency=RecurrenceFrequency.MONTHLY, interval=1)

    if re.search(r"\b(cada a[ñn]o|anualmente|todos los a[ñn]os)\b", text_lower):
        return RecurrenceRule(frequency=RecurrenceFrequency.YEARLY, interval=1)

    # Default: one-off
    return RecurrenceRule(frequency=RecurrenceFrequency.NONE)


# ──────────────────────────────────────────────────────────────────────────────
# Main parser
# ──────────────────────────────────────────────────────────────────────────────


def detect_intent(text: str) -> Intent:
    """Detect the user's intent from text. Returns UNKNOWN if no match."""
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                return intent
    return Intent.UNKNOWN


def extract_title(text: str, intent: Intent) -> str:
    """Extract the title/description from text by removing intent keywords."""
    title = text
    if intent == Intent.CREATE_REMINDER:
        title = re.sub(
            r"^(.*?)\b(recu[eé]rdame|av[ií]same|notif[ií]came|record[áa]me)\b\s*(que|de)?",
            "",
            title,
            flags=re.IGNORECASE,
        )
    elif intent == Intent.CREATE_TASK:
        title = re.sub(
            r"^(.*?)\b(tengo que|necesito|debo|tengo pendiente)\b\s*",
            "",
            title,
            flags=re.IGNORECASE,
        )
    elif intent == Intent.CREATE_MEMORY:
        title = re.sub(
            r"^(.*?)\b(guarda que|anota|memoriza|apunta que|registra que|recuerda que|recuerda el dato)\b\s*",
            "",
            title,
            flags=re.IGNORECASE,
        )
    elif intent == Intent.CREATE_LIST_ITEM:
        title = re.sub(
            r"^(.*?)\b(a[ñn]ade a la lista|agrega a la lista|pon en la lista)\b\s*",
            "",
            title,
            flags=re.IGNORECASE,
        )
    elif intent == Intent.DELETE_MEMORY:
        title = re.sub(
            r"^(.*?)\b(olvida que|borra (el )?recuerdo|elimina (la )?memoria)\b\s*",
            "",
            title,
            flags=re.IGNORECASE,
        )

    # Also remove date/time phrases for cleaner title
    title = re.sub(r"\b(mañana|pasado mañana|hoy)\b", "", title, flags=re.IGNORECASE)
    title = re.sub(
        r"\b(a\s+las?\s+\d{1,2}(?::\d{2})?(?:\s*(?:de\s+la\s+)?(?:tarde|noche|mañana))?)\b",
        "",
        title,
        flags=re.IGNORECASE,
    )
    title = re.sub(r"\b(cada\s+\w+)\b", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title).strip()
    title = re.sub(r"^[\s,:;-]+", "", title).strip()
    if title:
        title = title[0].upper() + title[1:]

    return title or "Recordatorio"


def parse(text: str, tz_name: str = "UTC", now: datetime | None = None) -> ParseSuccess | ParseFailure:
    """Parse natural language input into a structured operation.

    Args:
        text: User input text
        tz_name: IANA timezone name (e.g. "America/Caracas")
        now: Override current time (for testing)

    Returns:
        ParseSuccess with structured data, or ParseFailure if cannot parse.
        Caller should escalate ParseFailure to LLM.
    """
    if not text or not text.strip():
        return ParseFailure(
            intent=Intent.UNKNOWN,
            raw_text=text,
            reason="Empty input",
            suggestion="Escribe algo como 'Recuérdame mañana a las 9 revisar VNBOT'.",
        )

    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")

    if now is None:
        now = datetime.now(timezone.utc)
    now_local = now.astimezone(tz)

    intent = detect_intent(text)

    if intent == Intent.UNKNOWN:
        return ParseFailure(
            intent=Intent.UNKNOWN,
            raw_text=text,
            reason="No se detectó una intención reconocida",
            suggestion=(
                "Puedo ayudarte con: crear recordatorios ('Recuérdame...'), "
                "guardar memorias ('Guarda que...'), crear tareas ('Tengo que...'), "
                "o añadir a listas ('Añade a la lista...'). "
                "Para más capacidades, configura un proveedor LLM en Ajustes."
            ),
        )

    if intent == Intent.CREATE_REMINDER or intent == Intent.CREATE_TASK:
        return _parse_reminder(text, intent, tz, now_local)

    if intent == Intent.CREATE_MEMORY:
        return _parse_memory(text)

    if intent == Intent.CREATE_LIST_ITEM:
        return _parse_list_item(text)

    if intent in (
        Intent.QUERY_MEMORIES,
        Intent.LIST_REMINDERS,
        Intent.COMPLETE_REMINDER,
        Intent.DELETE_MEMORY,
    ):
        return ParseSuccess(
            intent=intent,
            raw_text=text,
            confidence=0.8,
            notes=["Heuristic detected intent; caller should execute appropriate query"],
        )

    return ParseFailure(
        intent=intent,
        raw_text=text,
        reason="Intent not yet implemented in heuristics",
    )


def _parse_reminder(
    text: str, intent: Intent, tz: ZoneInfo, now: datetime
) -> ParseSuccess | ParseFailure:
    """Parse a reminder or task creation request."""
    title = extract_title(text, intent)
    due_date = parse_relative_date(text, now, tz)
    time_tuple = parse_time(text, default_hour=9)
    recurrence = parse_recurrence(text)

    # If recurring but no specific date, default to tomorrow at 9am
    if due_date is None and recurrence.is_recurring():
        due_date = (now + timedelta(days=1)).astimezone(tz).replace(
            hour=9, minute=0, second=0, microsecond=0
        )

    if due_date is None:
        if time_tuple is not None:
            due_date = now.replace(hour=time_tuple[0], minute=time_tuple[1], second=0, microsecond=0)
            if due_date <= now:
                due_date = due_date + timedelta(days=1)
        else:
            return ParseFailure(
                intent=intent,
                raw_text=text,
                reason="No se detectó fecha ni hora",
                suggestion=(
                    "Prueba con: 'Recuérdame mañana a las 9 ...' o "
                    "'Avísame el lunes a las 3 de la tarde ...'"
                ),
            )

    if time_tuple is not None:
        due_date = due_date.replace(hour=time_tuple[0], minute=time_tuple[1], second=0, microsecond=0)

    if due_date <= now:
        return ParseFailure(
            intent=intent,
            raw_text=text,
            reason=f"La fecha detectada ({due_date.isoformat()}) ya pasó",
            suggestion="Especifica una fecha futura, como 'mañana' o 'el próximo lunes'.",
        )

    # Confidence: 1.0 if both date + time detected, 0.7 if only date (default time)
    confidence = 1.0 if time_tuple is not None else 0.7
    # But recurring without specific date/time is lower confidence
    if recurrence.is_recurring() and time_tuple is None and due_date is not None:
        confidence = 0.6

    return ParseSuccess(
        intent=intent,
        reminder=ParsedReminder(
            title=title,
            due_at=due_date,
            timezone=str(tz),
            recurrence=recurrence,
            confidence=confidence,
        ),
        raw_text=text,
        confidence=confidence,
        notes=["Heuristic parse" + (" (date+time)" if time_tuple else " (date only, default time)")],
    )


def _parse_memory(text: str) -> ParseSuccess:
    """Parse a memory creation request."""
    content = re.sub(
        r"^(.*?)\b(guarda que|anota|memoriza|apunta que|registra que|recuerda que|recuerda el dato)\b\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    content = re.sub(r"\s+", " ", content).strip()
    content = content[0].upper() + content[1:] if content else content

    tags = re.findall(r"#(\w+)", content)
    content = re.sub(r"#\w+", "", content).strip()

    return ParseSuccess(
        intent=Intent.CREATE_MEMORY,
        memory=ParsedMemory(
            content=content or "Memoria vacía",
            memory_type="note",
            tags=tags,
            confidence=0.9,
        ),
        raw_text=text,
        confidence=0.9,
    )


def _parse_list_item(text: str) -> ParseSuccess:
    """Parse a list item creation request."""
    item = re.sub(
        r"^(.*?)\b(a[ñn]ade a la lista|agrega a la lista|pon en la lista)\b\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    item = re.sub(r"\s+", " ", item).strip()

    return ParseSuccess(
        intent=Intent.CREATE_LIST_ITEM,
        memory=ParsedMemory(
            content=item or "Item vacío",
            memory_type="list_item",
            confidence=0.85,
        ),
        raw_text=text,
        confidence=0.85,
    )
