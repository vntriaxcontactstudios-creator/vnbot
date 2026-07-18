# VNBOT — Estrategia de Sincronización

> **Documento:** Estrategia de sincronización multi-dispositivo
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Diseño de sincronización
> **Fecha:** 2026-07-17
> **Documentos relacionados:** [TRD](./02-TRD-VNBOT.md), [Modelo de Datos](./07-MODELO-DATOS-VNBOT.md), [Seguridad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md), [App Flow](./06-APP-FLOW-VNBOT.md)

---

# 1. Propósito

Este documento define cómo VNBOT sincroniza datos entre múltiples dispositivos del mismo usuario. La sincronización es un requisito previo a la distribución multiplataforma (APK, Desktop, CLI) y debe estar diseñada y probada antes de que un usuario pueda acceder a sus datos desde más de un cliente.

Sin una estrategia de sync clara, VNBOT se arriesga a: pérdida de datos, duplicados silenciosos, conflictos irresolubles y una experiencia degradada en dispositivos móviles.

---

# 2. Principios de sincronización

## 2.1. Offline-first

VNBOT funciona completamente sin conexión. La sincronización es un mecanismo de transporte, no un requisito de operación. Si el servidor está caído, el usuario sigue creando memorias, recordatorios y listas localmente.

## 2.2. Sin pérdida de datos

Nunca se descarta silenciosamente una operación local. Si hay un conflicto, se presenta al usuario. Si hay un error de sync, se reintenta. Si no se puede resolver, se marca para intervención manual.

## 2.3. Conflicto visible, resolución por el usuario

Los conflictos no se resuelven con last-write-wins como política por defecto. El usuario siempre ve qué cambió en cada dispositivo y decide.

## 2.4. Cifrado en tránsito y en reposo

Las operaciones de sync siempre viajan sobre TLS 1.2+. Los datos pendientes de sync en el dispositivo se almacenan cifrados.

## 2.5. Idempotencia

Reenviar la misma operación no debe crear duplicados. Cada operación tiene un ID único por dispositivo.

---

# 3. Modelo de datos de sincronización

## 3.1. Version vectors

Cada dispositivo mantiene un version vector: un mapa de `{device_id → counter}` que representa el estado de conocimiento del dispositivo.

```text
Dispositivo A: {A: 5, B: 3}
Dispositivo B: {A: 3, B: 7}
```

Si A sync con B:
- A aprende que B está en counter 7.
- B aprende que A está en counter 5.
- Se intercambian las operaciones pendientes.

## 3.2. Operación de sync

Cada cambio local genera una `sync_operation`:

```json
{
  "op_id": "uuid-local-unique",
  "device_id": "device-A",
  "entity_type": "memory",
  "entity_id": "uuid-memory",
  "operation": "update",
  "payload": {"title": "nuevo título", ...},
  "base_version": 5,
  "timestamp": "2026-07-17T10:00:00Z"
}
```

## 3.3. Detección de conflictos

Un conflicto ocurre cuando:

1. El servidor recibe una operación con `base_version` que no coincide con la versión actual de la entidad.
2. Dos dispositivos envían operaciones para la misma entidad basadas en versiones diferentes.

```
Device A: edita memoria v3 → envía op(base: 3)
Device B: edita memoria v3 → envía op(base: 3)
Servidor: aplica A → versión es 4
Servidor: recibe B(base: 3) ≠ versión actual(4) → CONFLICTO
```

---

# 4. Estrategia de resolución

## 4.1. Reglas automáticas

Algunos conflictos se resuelven sin intervención del usuario:

| Tipo de conflicto | Resolución automática | Razón |
|---|---|---|
| Mismo campo, mismo valor | Ignorar | No hay diferencia real |
| Recordatorio completado en A, editado en B | Prevalece completado | La acción de completar es definitiva |
| Soft delete en A, editado en B | Prevalece delete, ofrece recuperar | El usuario confirmó el borrado |
| Campos diferentes en la misma entidad | Merge de campos no conflictivos | Cada campo es independiente |

## 4.2. Conflictos que requieren al usuario

| Tipo de conflicto | Presentación al usuario |
|---|---|
| Mismo campo con valores diferentes | Diff lado a lado con opción de elegir |
| Borrado hard en un dispositivo, edición en otro | Confirmación: "¿Eliminar definitivamente?" |
| Estructura cambiada (ej: lista reordenada) | Vista de ambas versiones + opción de fusión manual |

## 4.3. Flujo de resolución

```text
[Conflicto detectado]
        ↓
[Crear registro en sync_conflicts]
        ↓
[Notificar al usuario]
        ↓
[Mostrar diff: versión local vs versión remota]
        ↓
[Usuario elige: local | remota | fusionar | ambas]
        ↓
[Aplicar resolución]
        ↓
[Marcar conflicto como resuelto]
        ↓
[Re-sync]
```

---

# 5. Protocolo de sincronización

## 5.1. Push

```text
POST /api/v1/sync/push
Authorization: Bearer <token>
Content-Type: application/json

{
  "device_id": "device-A",
  "operations": [
    {"op_id": "...", "entity_type": "memory", "entity_id": "...", ...}
  ],
  "current_vector": {"A": 5, "server": 3}
}

Response:
{
  "accepted": 8,
  "conflicts": [
    {"entity_type": "memory", "entity_id": "...", "local": {...}, "remote": {...}}
  ],
  "server_vector": {"A": 5, "server": 8}
}
```

## 5.2. Pull

```text
POST /api/v1/sync/pull
Authorization: Bearer <token>
Content-Type: application/json

{
  "device_id": "device-A",
  "known_vector": {"A": 5, "server": 3}
}

Response:
{
  "operations": [
    {"op_id": "...", "entity_type": "reminder", "entity_id": "...", ...}
  ],
  "server_vector": {"A": 5, "server": 8},
  "has_more": false
}
```

## 5.3. Resolución de conflicto

```text
POST /api/v1/sync/conflicts/{id}/resolve
Authorization: Bearer <token>
Content-Type: application/json

{
  "resolution": "local" | "remote" | "merged" | "both",
  "merged_payload": {...}  // solo si resolution = "merged"
}
```

---

# 6. Entidades afectadas

| Entidad | Sync | Notas |
|---|---|---|
| memory_nodes | Sí | Con procedencia y confianza |
| memory_edges | Sí | Las edges derivadas se recalculan si es necesario |
| reminders | Sí | Los disparos locales se coordinan por timezone |
| reminders_recurring | Sí | Las instancias futuras se recalculan |
| lists | Sí | Con items |
| agents | Sí | Configuración del agente |
| skills | Sí | Versión de skill asignada |
| audit_logs | Solo server → cliente | No se sync de cliente a server |
| settings | Sí | Preferencias del usuario |
| credentials | No | Se reconfiguran por dispositivo |

---

# 7. Casos especiales

## 7.1. Recordatorios durante sync

- Si un recordatorio se crea en el dispositivo A y se sincroniza al servidor, el scheduler del servidor lo toma.
- Si el dispositivo A está offline, el scheduler local del dispositivo dispara el recordatorio.
- Si ambos schedulers disparan el mismo recordatorio, el servidor deduplica por `reminder_id + scheduled_time`.
- Las notificaciones se envían solo desde un punto (server wins si está disponible).

## 7.2. Borrado de memorias con relaciones

- Al borrar un nodo, sus edges se invalidan.
- Al sincronizar el borrado, el servidor propaga la invalidación.
- Si otro dispositivo creó edges nuevas mientras tanto, se marcan como "huérfanas" y se notifican al usuario.

## 7.3. Clock skew

- Todos los timestamps se normalizan a UTC en el servidor.
- Si el clock del dispositivo tiene drift > 5 minutos, se muestra una advertencia y se sugiere sincronizar la hora del dispositivo.
- Las operaciones se ordenan por version vector, no por timestamp.

---

# 8. Implementación por fase

| Fase | Sync |
|---|---|
| 0.1 MVP | No. Solo local. Los campos `version` y `updated_at` se preparan. |
| 0.2 Servidor | Sync server ↔ browser (misma máquina o red local). |
| 0.3 Plataformas | Sync multi-dispositivo completo con conflict resolution. |

---

# 9. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Conflictos frecuentes | Experiencia degradada | Minimizar con detección temprana y merge automático de campos |
| Queue local crece sin límite | Storage agotado | Límite de 10,000 ops pendientes. Alerta al usuario. |
| Sync parcial falla | Estado inconsistente | Transacciones por batch. Rollback automático. |
| Device perdido con ops pendientes | Datos perdidos | Las ops se descargan al server en el próximo sync de cualquier dispositivo. Si solo había un dispositivo, el backup local las contiene. |
| Performance con muchos dispositivos | Latencia alta | Sync es peer-to-server, no peer-to-peer. Un usuario típico tiene 2-3 dispositivos. |

---

# 10. Documentos relacionados

- [TRD](./02-TRD-VNBOT.md) — Arquitectura general.
- [Modelo de Datos](./07-MODELO-DATOS-VNBOT.md) — Entidades `sync_operations` y `sync_conflicts`.
- [App Flow](./06-APP-FLOW-VNBOT.md) — Flujos de resolución de conflictos.
- [Seguridad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md) — Seguridad de la sincronización.
- [Backend](./03-ESQUEMA-BACKEND-VNBOT.md) — Endpoints de sync.