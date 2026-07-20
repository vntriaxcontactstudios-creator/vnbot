"""VNBOT API — LLM infrastructure."""

from .router import LLMResult, parse_with_llm, _build_system_prompt, SYSTEM_PROMPT_TEMPLATE
from .providers import (
    ProviderConfig,
    ChainResult,
    call_provider,
    call_with_chain_fallback,
    get_provider_configs,
    get_enabled_providers,
    list_available_providers,
)
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
    # Router
    "LLMResult",
    "parse_with_llm",
    "_build_system_prompt",
    "SYSTEM_PROMPT_TEMPLATE",
    # Providers (multi-LLM — ADR-0012)
    "ProviderConfig",
    "ChainResult",
    "call_provider",
    "call_with_chain_fallback",
    "get_provider_configs",
    "get_enabled_providers",
    "list_available_providers",
    # Hermes learning loop
    "LearningResult",
    "background_review",
    "memory_curation",
    "skill_creation_check",
    "spawn_background_review",
    "MEMORY_MD_CAP_BYTES",
    "MAX_MEMORIES_PER_REVIEW",
    "MIN_MEMORY_CONFIDENCE",
    "CURATION_INTERVAL_HOURS",
    # Hermes persistence files
    "ensure_persistence_files",
    "materialize_memory_md",
    "materialize_user_md",
    "read_memory_md",
    "read_user_md",
    "user_md_path",
    "memory_md_path",
]



