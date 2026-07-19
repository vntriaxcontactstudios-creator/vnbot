# ADR-0005: Version vectors for sync (not last-write-wins)

## Estado

Aceptada

## Contexto

VNBOT se distribuirá en múltiples dispositivos (PWA, APK, desktop, CLI). Cada dispositivo puede crear, editar y borrar memorias y reminders offline. Cuando sincroniza, hay riesgo de conflictos:

- Dispositivo A edita memoria v3 → envía op(base: 3)
- Dispositivo B edita memoria v3 (mismo base) → envía op(base: 3)
- Server recibe A primero, aplica → v4
- Server recibe B con base=3 ≠ current=4 → CONFLICTO

**Last-write-wins (LWW)** es la estrategia más simple pero pierde datos silenciosamente — el último dispositivo que sincroniza sobrescribe los demás sin avisar al usuario.

## Decisión

**Adoptar version vectors (no LWW) para sync.** Reglas:

1. Cada dispositivo mantiene un vector `{device_id → counter}` representando su estado de conocimiento.
2. Toda entidad mutable tiene campos `version`, `updated_at`, `deleted_at`, `device_id`, `version_vector`, `is_conflict` desde el día 1 (incluso antes de implementar sync, útiles para auditoría y export).
3. Operación de sync incluye `base_version` para detectar conflictos.
4. Conflictos se resuelven con reglas automáticas + intervención del usuario:

**Reglas automáticas:**

| Conflicto | Resolución |
|-----------|------------|
| Mismo campo, mismo valor | Ignorar |
| Reminder completado en A, editado en B | Completado gana |
| Soft delete en A, editado en B | Delete gana, ofrecer recover |
| Campos diferentes en misma entidad | Merge no-conflictivo |

**Requiere usuario:**

| Conflicto | Presentación |
|-----------|--------------|
| Mismo campo diferente valor | Side-by-side diff, elegir |
| Hard delete en A, edit en B | "Eliminar definitivamente?" confirm |
| Cambio estructural (lista reordenada) | Ambas versiones + merge manual |

## Consecuencias

- **Positivas**: Cero pérdida silenciosa de datos, control del usuario sobre conflictos, base sólida para multi-device.
- **Negativas**: Mayor complejidad (sync engine, conflict UI), más campos en DB desde día 1.
- **Riesgos**: Conflictos frecuentes si usuario edita mismo dato en dos dispositivos — mitigar con merge por campo cuando es posible.

## Alternativas consideradas

1. **Last-write-wins (LWW)** — simple pero pierde datos silenciosamente. Inaceptable para un producto de memoria personal.
2. **CRDTs (Conflict-free Replicated Data Types)** — elegant pero complejo, librerías maduras solo para tipos básicos (text, counter). Para entidades estructuradas como MemoryNode no hay CRDT directo.
3. **Operational Transformation (OT)** — usado por Google Docs, pero requiere servidor central con secuenciación estricta. Overkill para VNBOT.

## Referencias

- TRD §24 #5 (frozen decision)
- Sync §3 (version vectors design), §4 (conflict resolution)
- Modelo de Datos §41 (sync fields from day 1)
