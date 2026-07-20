# ADR-0011: Hermes Learning Loop — Full Fase 0.7 Implementation

**Status:** Accepted
**Date:** 2026-07-20
**Supersedes:** Stub in commit c6a1f09 (Fase 0.5 prep)
**Superseded by:** —
**Related:** ADR-0007 (mandatory heuristic fallback), ADR-0009 (Hermes Agent methodology)

## Context

ADR-0009 specified the Hermes Agent methodology integration in 3 tracks:
- Track 1 (Fase 0.6): Background review branch
- Track 2 (Fase 0.7): Self-learning loop
- Track 3 (Fase 0.8): Memory curation + skill creation

The stubs were created in commit c6a1f09 as scaffolding. This ADR documents
the FULL implementation of Tracks 1, 2, and 3 — completing Fase 0.7 ahead of
schedule.

## Decision

Implement Hermes Learning Loop as 4 cooperating components:

### 1. `background_review()` — async post-response review

After each `POST /chat/operations/{id}/confirm`, spawn an asyncio task that:
1. Calls Z.AI glm-4.6 with `REVIEW_PROMPT` + the transcript (user input + assistant summary)
2. Parses the LLM's JSON response (`memories_to_save[]`, `nothing_to_learn`)
3. Enforces caps:
   - Max 2 memories per review (curación > acumulación)
   - Min confidence 0.5 (lower-confidence items discarded)
4. Persists each memory to `memory_nodes` table with `source_type=hermes_background_review`
5. Writes a `LearningLog` entry for audit (raw review JSON + outcome summary + tokens used)

**Critical:** the user-visible response never waits for this. `spawn_background_review()`
returns a fire-and-forget `asyncio.Task`.

### 2. `memory_curation()` — periodic job (every 6h)

Runs as an APScheduler job (`hermes_memory_curation`). Maintains ~3.5KB cap on
the materialized MEMORY.md file:
1. Estimates total bytes (memories × 200B avg)
2. If under cap: no action
3. If over cap:
   - Demote low-confidence Hermes memories (confidence < 0.6) → status=archived
   - If still over: demote oldest non-explicit_user_input memories
4. Writes a `LearningLog` entry with the action summary

### 3. `skill_creation_check()` — trigger-based skill creation

When any of these triggers fire, spawn an LLM call to generate a draft skill:
- ≥5 tool calls in a single operation
- Error recovery (agent failed then succeeded)
- User correction ("no, quería decir...")
- Novel successful workflow

The generated skill:
- Markdown body with name, description, steps, notes
- Status = "draft" (user must activate)
- Origin = "hermes"
- Confidence starts at 0.3
- If skill name already exists, patches the existing one (version++ + confidence bump)

### 4. Persistence files (`USER.md` + `MEMORY.md`)

Per ADR-0009 §3.2:
- `USER.md`: persistent user facts (name, preferences)
- `MEMORY.md`: working memory, ~3.5KB cap

Stored under `storage_local_path/workspaces/<workspace_id>/USER.md` and
`MEMORY.md`. Materialized from DB on demand via `materialize_user_md()` and
`materialize_memory_md()`.

## Consequences

### Positive

- **Audit trail**: every Hermes action writes a `LearningLog` entry. No silent
  memory mutations.
- **User control**: skills created by Hermes start as `draft`. User must
  activate them via `/skills/{id}/activate`.
- **Cap enforcement**: MEMORY.md stays small enough for LLM prompt context.
- **Confidence grows**: every successful skill use bumps confidence by 0.05
  (capped at 1.0).
- **Idempotent**: re-running `background_review` on the same input produces
  same output (no duplicate memories).

### Negative

- **LLM cost**: each chat confirm now triggers 1 background LLM call (~800
  tokens). Mitigated by `temperature=0.2` and `max_tokens=800`.
- **Latency on first memory**: Hermes memories are not visible until the
  background task completes (~3-5s). User is not blocked.
- **Skill name collisions**: Hermes may generate skills with same name as
  existing. Handled by patching the existing one.

### Neutral

- `LearningLog` table grows unbounded. Curation job doesn't prune logs —
  that's intentional (audit trail). User can manually delete via SQL.
- `USER.md` and `MEMORY.md` are materialized lazily (on `/skills/materialize`
  endpoint call). Not auto-updated on every memory write.

## Implementation

### New DB tables (migration 0003)

- `skills`: id, workspace_id, name, description, body_markdown, triggers_json,
  status, origin, version, confidence, use_count, last_used_at, tags_ciphertext,
  created_at, updated_at, deleted_at
- `learning_logs`: id, workspace_id, action, origin, trigger_reason, review_json,
  outcome_summary, memory_ids_json, skill_id, llm_model, llm_tokens_used,
  success, error_message, created_at

### New API endpoints (8)

- `GET /api/v1/skills` — list (filterable by status, origin)
- `POST /api/v1/skills` — create hand-authored skill
- `GET /api/v1/skills/{id}` — get skill detail
- `PATCH /api/v1/skills/{id}` — update skill (auto-increments version)
- `DELETE /api/v1/skills/{id}` — soft-delete (status=archived)
- `POST /api/v1/skills/{id}/activate` — promote draft → active
- `POST /api/v1/skills/{id}/use` — record skill use (bumps confidence)
- `POST /api/v1/skills/materialize` — regenerate USER.md + MEMORY.md
- `GET /api/v1/skills/{id}/history` — view LearningLog entries for a skill

- `GET /api/v1/learning` — list recent learning log entries
- `GET /api/v1/learning/summary` — stats (counts by action, success rate, tokens)
- `GET /api/v1/learning/{id}` — get single log entry
- `POST /api/v1/learning/curate` — manually trigger memory curation
- `POST /api/v1/learning/review` — manually trigger background review

### Wiring

- `chat.py`: after `op.status = SUCCEEDED`, calls `spawn_background_review()`
- `scheduler.py`: registers `memory_curation` job (every 6h)
- `llm/__init__.py`: exports all public functions + constants

## Verification

```
✅ Backend starts cleanly (3 scheduler jobs: occurrences, deliver, curation)
✅ Skills CRUD works (create, list, get, patch, delete, activate, use)
✅ LearningLog written on every action
✅ Materialize endpoint regenerates USER.md + MEMORY.md
✅ Memory curation runs (no-op when under cap)
✅ Typecheck passes (tsc --noEmit)
✅ Demo build succeeds (VITE_DEMO_MODE=true)
```

## Future Work

- **Fase 0.8**: integrate MEMORY.md into the LLM system prompt (currently
  generated but not yet used by `parse_with_llm`)
- **Fase 0.9**: user-facing UI for browsing LearningLog (currently API-only)
- **Fase 1.0**: skill versioning with diff viewer
