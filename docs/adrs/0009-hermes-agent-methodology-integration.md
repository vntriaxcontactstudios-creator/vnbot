# ADR-0009: Hermes Agent methodology integration for self-improving skills

## Estado

Propuesta (para implementación en Fase 0.7)

## Contexto

VNBOT tiene planificada la Fase 0.7 (Skills y agentes) según el Roadmap (docs/10 §12). Hasta ahora, las skills definidas en `skills/README.md` son estáticas: manifest YAML + input/output schema + instructions. No hay mecanismo para que VNBOT aprenda de la experiencia ni mejore sus skills con el uso.

**Hermes Agent** (`NousResearch/hermes-agent`, 218k★, MIT) es un agente de IA autoperfeccionable que implementa una metodología de "mejora y aprendizaje" mediante:

1. **Background review fork** — después de cada respuesta, un LLM call separado revisa el transcript y decide qué persistir. El usuario nunca espera por el aprendizaje.
2. **Skill creation automática** — cuando se detectan patrones (≥5 tool calls, recovery de errores, correcciones del usuario), el agente escribe un archivo de skill.
3. **Skill self-improvement** — skills existentes se patchean con cambios dirigidos (old→new string), no reescrituras completas.
4. **Memory curation periódica** — prompt interno a intervalos que curta `MEMORY.md` con cap de ~3.5KB, forzando curación sobre acumulación.
5. **Progressive disclosure** — solo carga nombres de skills por defecto; contenido completo bajo demanda → coste de tokens plano sin importar cuántas skills haya.
6. **Four-layer memory** — prompt memory (always-on) + FTS5 session search + skills (procedural) + user modeling.
7. **DSPy + GEPA** — evolución genética pareto offline para optimizar skills/prompts sin GPU (~$2-10/run).

Hermes usa MCP como protocolo de tools (first-class), tiene un catálogo curado de MCP servers, y un Skills Hub comunitario basado en el estándar abierto `agentskills.io`.

El usuario preguntó explícitamente si esta metodología podría integrarse con VNBOT.

## Decisión

**Adoptar Track 1 + Track 2 selectivo de la metodología Hermes para la Fase 0.7 de VNBOT.**

### Track 1 — Adoptar estándares abiertos (Fase 0.7 inicial)

1. **`agentskills.io` como formato de skills de VNBOT**: las skills de VNBOT usarán el formato markdown con front-matter del estándar `agentskills.io` (name, description, version, platforms, tags, requires_toolsets). Esto hace las skills de VNBOT compatibles con el Skills Hub comunitario de Hermes, Claude Code, Cursor y Codex.

2. **MCP como protocolo de tools de VNBOT** (ya planificado en docs/09): adoptar el patrón de catálogo curado de Hermes — los usuarios pueden instalar MCP servers con `vnbot mcp install <name>` desde un catálogo revisado.

3. **Hermes Function-Calling ChatML format**: si VNBOT usa modelos open-source (Ollama, llama.cpp), adoptar el formato `<tools>` JSON schemas de Hermes para tool use.

### Track 2 — Portear el learning loop (Fase 0.7 avanzada)

4. **Background review fork**: después de cada respuesta del chat, VNBOT spawn un LLM call separado (async, background) con:
   - El transcript de la conversación
   - Tools limitados a: `memory.save`, `memory.update`, `skill.create`, `skill.patch`
   - Un prompt del sistema que le dice: "Revisa esta conversación. ¿Hay algo que valga la pena recordar? ¿Se puede crear o mejorar una skill?"
   - El usuario nunca espera por esto — es completamente asíncrono.

5. **Skill-creation triggers**: detectar automáticamente cuándo crear skills:
   - ≥5 tool calls en una sola operación
   - Recovery de errores (el agente falló y luego tuvo éxito)
   - Corrección del usuario ("no, quería decir...")
   - Workflow no obvio que funcionó

6. **`skill_manage` tool**: implementar como MCP tool interna con operaciones:
   - `create` — crear nueva skill (agentskills.io format)
   - `patch` — cambio dirigido old→new string (preferido sobre reescritura)
   - `edit` — reescritura completa (usar con precaución)
   - `delete` — eliminar skill
   - `write_file` / `remove_file` — gestión de archivos dentro de la skill

7. **Memory curation periódica**: scheduler job que ejecuta un prompt de curación:
   - Lee `MEMORY.md` actual + actividad reciente
   - Decide qué mantener, qué comprimir, qué eliminar
   - Cap de ~3.5KB para forzar curación
   - Ejecuta cada N horas o N interacciones

8. **Progressive disclosure para skills**:
   - Por defecto, solo cargar `name` + `description` de cada skill en el system prompt
   - Cuando el LLM necesita una skill, hacer RAG/FTS5 search para cargar el contenido completo
   - Coste de tokens plano sin importar si hay 10 o 200 skills

9. **Four-layer memory**:
   - Layer 1: `MEMORY.md` (always-on, ~3.5KB, curada)
   - Layer 2: FTS5 session search (ya implementado para memories, extender a conversaciones)
   - Layer 3: Skills como procedural memory (agentskills.io format)
   - Layer 4: User modeling (opcional, post-MVP — preferencias + patrones del usuario)

### Track 3 — Reuse directo (post-1.0, exploratorio)

10. **`hermes-agent-self-evolution`** (MIT): usar DSPy + GEPA para optimizar skills/prompts de VNBOT offline. Ejecutar como job programado (weekly/monthly). Requiere:
    - Test suite que validar que las skills optimizadas siguen funcionando
    - Human PR review (nunca auto-commit)
    - ~$2-10/run en API costs

## Consecuencias

- **Positivas**:
  - VNBOT aprende de cada interacción sin que el usuario espere
  - Skills compatibles con el ecosistema Hermes/Claude/Cursor/Codex
  - MCP da acceso instantáneo al catálogo comunitario
  - Memory curation evita que la memoria se convierta en un dump
  - Progressive disclosure mantiene coste de tokens plano
- **Negativas**:
  - Complejidad adicional en el backend (background fork, skill_manage, curation scheduler)
  - Coste de API adicional (cada conversación genera 2 LLM calls: respuesta + review)
  - Riesgo de skills mal generadas (mitigar con validation + human review opcional)
- **Riesgos**:
  - Skill hallucination: el LLM podría crear skills incorrectas → mitigar con test suite + `skill_manage` validation
  - Memory loss: la curación podría eliminar algo importante → mitigar con versioning + undo
  - Token cost growth: si hay muchas skills, el progressive disclosure debe ser eficiente → mitigar con FTS5 search

## Alternativas consideradas

1. **Solo Track 1 (solo estándares, sin learning loop)** — rechazada porque pierde el valor principal (auto-mejora)
2. **Solo Track 3 (reuse directo de Hermes)** — rechazada por coupling excesivo con Hermes
3. **Implementar learning loop desde cero sin参考 Hermes** — rechazada por reinventar la rueda; Hermes ya validó el patrón con 218k★
4. **No integrar nada de Hermes** — rechazada; el usuario lo pidió explícitamente y el valor es claro

## Implementación

### Fase 0.7 — Sprint 1 (Track 1)
- [ ] Migrar skills/ a formato `agentskills.io` (markdown + front-matter)
- [ ] Implementar `skill_manage` MCP tool (create/patch/edit/delete)
- [ ] Progressive disclosure: cargar solo name+description por defecto
- [ ] Skill store: `~/.vnbot/skills/` con FTS5 search

### Fase 0.7 — Sprint 2 (Track 2 core)
- [ ] Background review fork: async LLM call post-response con tool whitelist
- [ ] Skill-creation triggers: ≥5 tool calls, error recovery, user correction
- [ ] Memory curation scheduler job (cada 6h o 50 interacciones)

### Fase 0.7 — Sprint 3 (Track 2 avanzado)
- [ ] Four-layer memory: separar prompt memory de session search
- [ ] MEMORY.md con cap de 3.5KB
- [ ] User modeling layer (opcional)

### Post-1.0 (Track 3 exploratorio)
- [ ] Spike: hermes-agent-self-evolution con DSPy + GEPA contra skills de VNBOT
- [ ] Test suite de skills para validar optimizaciones
- [ ] Human PR review workflow

## Referencias

- NousResearch/hermes-agent: https://github.com/NousResearch/hermes-agent (MIT, 218k★)
- NousResearch/hermes-agent-self-evolution: https://github.com/NousResearch/hermes-agent-self-evolution (MIT)
- agentskills.io: estándar abierto para skills portátiles
- docs/09-MCP-Y-SKILLS-VNBOT.md: arquitectura MCP planificada de VNBOT
- docs/10-ROADMAP-VNBOT.md §12: Fase 0.7 Skills y agentes
- ADR-0004: MCP is protocol, not authorization
- ADR-0007: Mandatory heuristic fallback before depending on LLM
- ADR-0008: Single-user personal assistant
