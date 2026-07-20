"""VNBOT API — LLM infrastructure."""

from .router import LLMResult, parse_with_llm, _build_system_prompt, SYSTEM_PROMPT_TEMPLATE
from .learning_loop import (
    LearningResult,
    background_review,
    memory_curation,
    skill_creation_check,
    spawn_background_review,
    MEMORY_MD_CAP_BYTES,
    MAX_MEMORIES_PER_REVIEW,
    MIN_MEMORY_CONFIDENCE,
    CURATION_INTERVAL_HOURS,
)
from .hermes_files import (
    ensure_persistence_files,
    materialize_memory_md,
    materialize_user_md,
    read_memory_md,
    read_user_md,
    user_md_path,
    memory_md_path,
)

__all__ = [
    "LLMResult",
    "parse_with_llm",
    "_build_system_prompt",
    "SYSTEM_PROMPT_TEMPLATE",
    "LearningResult",
    "background_review",
    "memory_curation",
    "skill_creation_check",
    "spawn_background_review",
    "MEMORY_MD_CAP_BYTES",
    "MAX_MEMORIES_PER_REVIEW",
    "MIN_MEMORY_CONFIDENCE",
    "CURATION_INTERVAL_HOURS",
    "ensure_persistence_files",
    "materialize_memory_md",
    "materialize_user_md",
    "read_memory_md",
    "read_user_md",
    "user_md_path",
    "memory_md_path",
]


