# ADR-0007: Mandatory heuristic fallback before depending on LLM

## Estado

Aceptada

## Contexto

VNBOT depende de LLMs para interpretar lenguaje natural. Pero los LLMs pueden fallar por:

- Caída del proveedor (Z.AI, OpenAI, Anthropic tienen outages).
- Rate limit agotado (30 RPM en Z.AI free tier).
- Sin conexión a internet (modo offline).
- Usuario no quiere configurar LLM (privacy mode).

Si VNBOT **solo** funciona con LLM, se vuelve inutilizable en cualquiera de estos escenarios. Para un producto de memoria personal y recordatorios confiables, esto es inaceptable.

## Decisión

**Heurísticas obligatorias como fallback antes de depender del LLM.** Reglas:

1. **Chain de fallback:** primary (LLM) → secondary (otro LLM) → local (Ollama) → **heuristics** → error amigable.
2. **Heurísticas cubren casos comunes** (PRD §18):
   - Crear reminder: regex + natural date/time parse
   - Crear memoria: captura directa
   - Query memories: exact + fuzzy text
   - List reminders
   - Complete reminder (match by ID o partial text)
   - Create list (structured command)
3. **Detección por palabras clave:**
   - "Recuérdame", "Avísame" → reminder
   - "Tengo que", "Necesito", "Debo" → task
   - "Guarda que", "Anota" → memory
   - "Olvida que" → delete memory
   - "Añade a la lista" → list item
4. **Fechas relativas:** "mañana" → tomorrow 10:00, "próximo lunes" → next Monday 09:00.
5. **Cuando no puede interpretar, debe responder:**
   > *"No pude interpretar eso sin un modelo de IA conectado. [Instrucciones para configurar un proveedor]."*
6. **Heurísticas NO deben** (PRD §18.2):
   - Inferir relaciones entre memorias
   - Interpretar imágenes/audio
   - Generar briefings
   - Operar MCP tools
   - Manejar contexto multi-turn complejo

## Consecuencias

- **Positivas**: Producto utilizable 100% offline o sin LLM, robustez ante outages, transparencia (el usuario sabe cuándo se usa LLM vs heurística).
- **Negativas**: Experiencia limitada sin LLM (no todas las features), más código de parser.
- **Riesgos**: Heurísticas demasiado agresivas pueden crear reminders incorrectos — mitigar con confirmación siempre (`waiting_confirmation` state).

## Alternativas consideradas

1. **Solo LLM** — inaceptable, producto no funciona offline.
2. **Solo heurísticas (no LLM)** — experiencia demasiado limitada para valor real del producto.
3. **Heurísticas opcionales** — no cumple con "recordatorios confiables" del tagline.

## Referencias

- TRD §24 #12 (frozen decision)
- PRD §18 (heuristic fallback spec, 20+ input cases)
- Plan §4 (Phase 0 preparation: heuristics mandatory)
- ADR relacionado: ADR-0003 (no ZK claim with cloud LLM)
