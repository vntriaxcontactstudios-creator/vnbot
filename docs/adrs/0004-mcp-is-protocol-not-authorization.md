# ADR-0004: MCP is protocol, not authorization

## Estado

Aceptada

## Contexto

El Model Context Protocol (MCP) de Anthropic es un protocolo de transporte para que los agentes LLM invoquen herramientas externas. Sin embargo, MCP por sí mismo **no** es un sistema de autorización — solo dice "cómo llamar a la tool", no "si está permitido llamarla".

Si VNBOT confundiera MCP con autorización, cualquier tool descubierta vía MCP podría ejecutarse automáticamente, abriendo vectores de prompt injection y escalation.

## Decisión

**MCP es protocolo (transporte), no autorización.** Separación estricta:

1. **MCP Gateway** — descubre tools, mantiene handshake, transporta requests/responses, aplica timeouts y rate limits.
2. **Policy Engine** (separado) — decide si una tool puede ejecutarse basándose en:
   - Identidad del usuario y workspace
   - Rol del usuario (owner/admin/member/viewer)
   - Permisos del agente (no hereda los del usuario)
   - Permisos de la skill (`deny/read/write/execute/admin`)
   - Scopes de la tool (`graph.read`, `memory.write`, `email.send`, etc.)
   - Risk tier de la operación (bajo/medio/alto/crítico)
   - Política de confirmación (auto/required_if_ambiguous/always)

Reglas de oro:

- Tools descubiertas vía MCP nunca se auto-habilitan: `DISCOVERED → REVIEW_REQUIRED → ENABLED/DISABLED`.
- Un agente no puede escalar sus propios permisos.
- Un agente no hereda los permisos del usuario — solo recibe los explícitamente asignados.
- `email.send`, `filesystem.write`, `memory.delete_many`, `calendar.delete_event` requieren confirmación fuerte.

## Consecuencias

- **Positivas**: Defensa en profundidad contra prompt injection y escalación, auditoría clara, control del usuario.
- **Negativas**: Más fricción (confirmaciones), más código (policy engine separado).
- **Riesgos**: Policy engine muy restrictivo puede frustrar usuarios — equilibrar con UX de "trust on first use" por workspace.

## Alternativas consideradas

1. **Auto-habilitar tools MCP** — inaceptable, viola principio "deny by default".
2. **Delegar autorización al LLM** — inaceptable, LLM no es security boundary.
3. **Política global "permit_all"** — inaceptable, no respeta scopes ni risk tiers.

## Referencias

- TRD §24 #10 (frozen decision)
- MCP §2 (architecture), §6.2 (DISCOVERED → REVIEW_REQUIRED flow)
- Seguridad §8 (policy engine), §11 (prompt injection)
- ADR relacionado: ADR-0007 (mandatory heuristic fallback)
