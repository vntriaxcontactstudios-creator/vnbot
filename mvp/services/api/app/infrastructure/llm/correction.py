"""VNBOT API — User correction detection (Fase 0.9 ADR-0009 Track 2).

Per ADR-0009: skill_creation_check should fire when the user corrects the
assistant. This module detects "user correction" patterns in chat input:

Triggers:
  - Explicit negation + correction: "no, quería decir...", "no, es..."
  - Direct correction: "es X, no Y", "mejor dicho X"
  - Rejection of proposal: "no es eso", "está mal", "incorrecto"
  - Repetition with different content: user asks same thing 2x with different words

Returns a CorrectionResult that skill_creation_check can use to spawn skill
creation (if other triggers also fire, or alone if pattern is strong).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("vnbot.api.learning.correction")

# Patterns that indicate user correction (regex, case-insensitive, Spanish + English)
CORRECTION_PATTERNS = [
    # Spanish: "no, quería decir...", "no, es..."
    r"\bno[,.]?\s+(quería|quiero|quisiera)\s+(decir|expresar)",
    r"\bno[,.]?\s+es\s+(eso|eso mismo|así)",
    r"\bmejor\s+dicho\b",
    r"\bo\s+sea\b",
    r"\bme\s+expreso\s+mal\b",
    r"\bperdón[,.]?\s+(quería|es)\s+",
    r"\bdisculpa[,.]?\s+(quería|es)\s+",
    r"\bno[,.]?\s+me\s+refiero\s+a\s+(eso|eso)",
    r"\bestá\s+(mal|incorrecto|equivocado)\b",
    r"\bno\s+es\s+correcto\b",
    # English fallbacks
    r"\bno[,.]?\s+I\s+meant\b",
    r"\bactually[,.]?\s+\b",
    r"\bthat'?s\s+(wrong|not\s+right|incorrect)\b",
    r"\bsorry[,.]?\s+I\s+meant\b",
    r"\bbetter\s+said:\s*\b",
]

# Compile patterns once
_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in CORRECTION_PATTERNS]


@dataclass
class CorrectionResult:
    """Result of user correction detection."""

    is_correction: bool
    confidence: float  # 0.0-1.0
    matched_pattern: str | None = None
    pattern_index: int = -1


def detect_user_correction(text: str) -> CorrectionResult:
    """Detect if the user's input is a correction of a previous response.

    Args:
        text: The user's input text

    Returns:
        CorrectionResult with is_correction=True if a pattern matched
    """
    if not text or len(text.strip()) < 3:
        return CorrectionResult(is_correction=False, confidence=0.0)

    text_lower = text.lower().strip()

    # Check each pattern
    for idx, pattern in enumerate(_COMPILED_PATTERNS):
        match = pattern.search(text)
        if match:
            matched_text = match.group(0)
            logger.debug(
                f"[correction] matched pattern #{idx}: '{matched_text}' in: {text[:80]!r}"
            )
            # Confidence: 0.7 for explicit corrections, 0.5 for softer ones
            confidence = 0.7 if idx < 10 else 0.5
            return CorrectionResult(
                is_correction=True,
                confidence=confidence,
                matched_pattern=matched_text,
                pattern_index=idx,
            )

    return CorrectionResult(is_correction=False, confidence=0.0)


async def maybe_trigger_skill_creation_on_correction(
    user_input: str,
    workspace_id: str = "00000000-0000-0000-0000-000000000001",
    context_summary: str = "",
) -> str | None:
    """If user correction detected, fire skill_creation_check.

    Returns the new skill_id if a skill was created, or None.
    """
    from .learning_loop import skill_creation_check

    correction = detect_user_correction(user_input)
    if not correction.is_correction:
        return None

    logger.info(
        f"[correction] detected (conf={correction.confidence:.2f}, "
        f"pattern={correction.matched_pattern!r}) — firing skill_creation_check"
    )

    # Use the correction as context for skill creation
    context = context_summary or f"User correction: {user_input[:300]}"
    skill_id = await skill_creation_check(
        tool_calls_count=0,  # correction alone is a trigger, not tool calls
        error_recovered=False,
        user_corrected=True,
        novel_workflow=False,
        workspace_id=workspace_id,
        context_summary=context,
    )
    return skill_id
