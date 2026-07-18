# VNBOT — Esquema Backend

> **Documento:** Esquema Backend
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Diseño de backend
> **Fecha:** 2026-07-16
> **Documentos relacionados:** [PRD](./01-PRD-VNBOT.md), [TRD](./02-TRD-VNBOT.md), [Modelo de Datos](./07-MODELO-DATOS-VNBOT.md), [Seguridad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md)

---

# 1. Propósito

Este documento especifica la estructura del backend de VNBOT: servicios, módulos, entidades, API, eventos, trabajos asíncronos, scheduler, memoria, grafo, agentes, MCP, notificaciones, archivos, healthchecks, errores y reglas de seguridad.

El backend debe soportar cuatro formas de ejecución:

1. **Local:** un usuario, SQLite y servicios mínimos.
2. **Servidor personal:** varios dispositivos, PostgreSQL, Redis y workers.
3. **Servidor multiusuario:** workspaces aislados y servicios replicables.
4. **Modo híbrido:** datos locales con sincronización opcional.

La regla de diseño más importante es:

```text
El cliente solicita.
La API autentica y valida.
El dominio decide.
La cola ejecuta trabajos durables.
Las integraciones actúan con permisos.
La auditoría registra el resultado.
```

---

# 2. Objetivos del backend

## 2.1. Objetivos funcionales

- Gestionar usuarios, sesiones y workspaces.
- Procesar mensajes de chat.
- Interpretar intenciones mediante LLM o heurística.
- Guardar memorias y relaciones.
- Consultar el grafo personal.
- Crear recordatorios persistentes.
- Ejecutar notificaciones sin duplicados.
- Procesar audio y archivos de forma asíncrona.
- Gestionar agentes y skills.
- Conectar herramientas MCP.
- Mantener auditoría de acciones.
- Exportar e importar datos.
- Exponer healthchecks.

## 2.2. Objetivos operativos

- Poder reiniciar API y workers sin perder trabajos confirmados.
- Permitir reintentos seguros.
- Poder sustituir SQLite por PostgreSQL.
- Poder reemplazar Redis por una implementación local limitada.
- Poder añadir proveedores LLM sin cambiar la lógica de dominio.
- Poder añadir integraciones como plugins/adaptadores.
- Poder ejecutar la aplicación en Docker.

## 2.3. No objetivos del backend inicial

- Ejecutar código arbitrario del usuario.
- Automatización financiera.
- Scraping de cuentas personales.
- Escucha permanente del micrófono.
- Acceso universal al filesystem.
- Envío automático de mensajes a terceros sin consentimiento.
- Orquestación multiagente totalmente autónoma.

---

# 3. Arquitectura de servicios

## 3.1. Vista general

```text
                    ┌───────────────────┐
                    │ Web / APK / Tauri │
                    │       / CLI       │
                    └─────────┬─────────┘
                              │ HTTPS / WebSocket / IPC
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         VNBOT API                           │
│ Auth · Chat · Memory · Graph · Reminders · Agents · Admin   │
└──────┬───────────────┬───────────────┬──────────────────────┘
       │               │               │
       ▼               ▼               ▼
┌────────────┐  ┌──────────────┐  ┌─────────────────┐
│ PostgreSQL │  │ Redis / Queue│  │ Object Storage  │
│ SQLite     │  │ locks/cache  │  │ MinIO / S3      │
└────────────┘  └──────┬───────┘  └─────────────────┘
                       │
              ┌────────▼────────┐
              │ Worker/Scheduler │
              │ audio · jobs ·   │
              │ reminders · sync │
              └────────┬─────────┘
                       │
             ┌─────────▼─────────┐
             │ MCP Gateway / LLM │
             │ Router / Channels │
             └───────────────────┘
```

## 3.2. Servicios del MVP

### `vnbot-api`

Servicio HTTP principal. Gestiona autenticación, comandos, consultas, confirmaciones, memoria, recordatorios y administración.

### `vnbot-worker`

Procesa tareas largas o reintentables:

- Audio.
- Embeddings.
- Notificaciones.
- Consolidación.
- Backups.
- Sincronización.

### `vnbot-scheduler`

Calcula qué ocurrencias de recordatorios deben encolarse. Debe ejecutarse como instancia única o usar locks distribuidos.

### `vnbot-mcp-gateway`

Gestiona servidores MCP externos, schemas, scopes, timeouts, policy engine y auditoría.

En una instalación local estos servicios pueden ejecutarse dentro de un proceso supervisado, pero deben mantener límites de módulos claros.

## 3.3. Servicios posteriores

- `notification-service` dedicado.
- `transcription-service` separado si se necesita GPU.
- `embedding-service` local.
- `sync-service` multi-dispositivo.
- `community-plugin-registry`.
- `observability-stack`.

No se deben extraer microservicios únicamente por moda. La separación se hará cuando exista una necesidad de escalado, seguridad o aislamiento.

---

# 4. Estructura de módulos del API

```text
services/api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── middleware/
│   │   ├── auth.py
│   │   ├── request_id.py
│   │   ├── rate_limit.py
│   │   └── error_handler.py
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── chat.py
│   │       ├── memories.py
│   │       ├── graph.py
│   │       ├── reminders.py
│   │       ├── agents.py
│   │       ├── skills.py
│   │       ├── integrations.py
│   │       ├── audio.py
│   │       ├── files.py
│   │       ├── exports.py
│   │       └── health.py
│   ├── domain/
│   │   ├── memories/
│   │   ├── reminders/
│   │   ├── agents/
│   │   ├── operations/
│   │   └── policies/
│   ├── application/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── services/
│   ├── infrastructure/
│   │   ├── db/
│   │   ├── queue/
│   │   ├── llm/
│   │   ├── mcp/
│   │   ├── storage/
│   │   └── notifications/
│   └── schemas/
├── migrations/
└── tests/
```

## 4.1. Regla de dependencias

```text
api → application → domain
infrastructure → application/domain ports
```

El dominio no debe importar FastAPI, Redis, SQLAlchemy, proveedores LLM ni SDKs externos.

---

# 5. Contextos de dominio

## 5.1. Identity Context

Gestiona:

- Usuarios.
- Sesiones.
- Workspaces.
- Roles.
- MFA posterior.
- Recuperación de cuenta.

## 5.2. Memory Context

Gestiona:

- Memorias.
- Nodos.
- Aristas.
- Procedencia.
- Confianza.
- Sensibilidad.
- Expiración.
- Correcciones.
- Borrado.

## 5.3. Reminder Context

Gestiona:

- Recordatorios.
- Reglas de recurrencia.
- Ocurrencias.
- Canales.
- Estados de entrega.
- Posponer/completar/cancelar.

## 5.4. Agent Context

Gestiona:

- Agentes.
- Prompts.
- Modelos.
- Skills.
- Presupuestos.
- Nivel de autonomía.
- Herramientas y permisos.

## 5.5. Operation Context

Gestiona el ciclo de vida de toda acción iniciada por usuario o agente.

## 5.6. Integration Context

Gestiona:

- Integraciones.
- OAuth.
- Tokens.
- Scopes.
- Healthchecks.
- Revocación.

## 5.7. File Context

Gestiona:

- Audios.
- Imágenes.
- Documentos.
- Retención.
- Cifrado.
- Referencias a memorias.

---

# 6. Identidad, usuarios y workspaces

## 6.1. Usuario

```text
User
- id
- email nullable en modo local
- display_name
- password_hash nullable
- timezone
- locale
- status
- created_at
- updated_at
```

## 6.2. Workspace

Un workspace separa contextos y permisos.

Ejemplos:

- Personal.
- Trabajo.
- Estudio.
- Familia.
- Proyecto VNBOT.

```text
Workspace
- id
- owner_user_id
- name
- type
- settings_json
- created_at
- updated_at
```

## 6.3. Roles

```text
owner
admin
member
viewer
```

El modo personal puede utilizar solo `owner`, pero el modelo debe permitir expansión.

## 6.4. Autorización

Cada endpoint debe obtener el workspace desde la sesión y verificar que el recurso pertenece a dicho workspace. Nunca se debe aceptar solamente un `workspace_id` enviado por el cliente.

---

# 7. Modelo de operaciones

## 7.1. Propósito

Una operación representa una intención completa: crear un recordatorio, guardar una memoria, ejecutar una herramienta o procesar audio.

```text
Operation
- id
- workspace_id
- user_id
- agent_id nullable
- type
- status
- input_ref
- output_ref
- risk_level
- requires_confirmation
- confirmed_at
- created_at
- updated_at
- expires_at
```

## 7.2. Estados

```text
RECEIVED
CLASSIFYING
PROPOSED
NEEDS_CLARIFICATION
WAITING_CONFIRMATION
QUEUED
EXECUTING
SUCCEEDED
RETRYING
FAILED
CANCELLED
EXPIRED
```

## 7.3. Idempotencia

Cada comando mutable acepta `Idempotency-Key`.

Ejemplo:

```http
POST /api/v1/reminders
Idempotency-Key: reminder-create-9f43
```

La API debe guardar el resultado asociado a la clave durante un periodo definido. Si llega la misma operación, devuelve el resultado original en lugar de crear otro recurso.

## 7.4. Expiración

Las propuestas de confirmación deben caducar. Una acción confirmada demasiado tarde debe volver a validarse, especialmente si contiene una fecha, precio, disponibilidad o permiso externo.

---

# 8. API pública versionada

Base:

```text
/api/v1
```

Formato general de respuesta exitosa:

```json
{
  "data": {},
  "meta": {
    "request_id": "req_123",
    "operation_id": "op_123"
  }
}
```

Formato general de error:

```json
{
  "error": {
    "code": "REMINDER_AMBIGUOUS_TIME",
    "message": "Falta la hora del recordatorio",
    "details": {
      "field": "due_at"
    },
    "retryable": false,
    "request_id": "req_123"
  }
}
```

---

# 9. Endpoints de autenticación

## `POST /auth/register`

Crea una cuenta en un servidor remoto.

Entrada:

```json
{
  "email": "usuario@example.com",
  "password": "...",
  "display_name": "Usuario"
}
```

Requisitos:

- Validar email.
- Aplicar rate limit.
- Hash Argon2id.
- No revelar si un email existe en contextos sensibles.
- Enviar verificación si el despliegue lo requiere.

## `POST /auth/login`

Crea sesión segura y devuelve cookies o tokens según el cliente.

## `POST /auth/logout`

Revoca la sesión actual.

## `POST /auth/refresh`

Rota refresh token cuando aplique.

## `GET /auth/me`

Devuelve usuario y workspaces permitidos, nunca secretos.

## `POST /auth/lock`

Bloquea la bóveda de la sesión local o solicita reautenticación.

---

# 10. Endpoints de chat

## `POST /chat`

Entrada:

```json
{
  "conversation_id": "conv_123",
  "agent_id": "agent_default",
  "content": "Recuérdame pagar la electricidad mañana a las 8",
  "attachments": [],
  "client_context": {
    "timezone": "America/Caracas",
    "platform": "web"
  }
}
```

Proceso:

1. Validar usuario y workspace.
2. Crear mensaje.
3. Crear operación.
4. Clasificar intención.
5. Recuperar contexto autorizado.
6. Generar propuesta estructurada.
7. Evaluar riesgo.
8. Responder con texto y/o `operation_id`.

Respuesta posible:

```json
{
  "data": {
    "message_id": "msg_123",
    "operation_id": "op_123",
    "assistant_text": "Puedo recordarte pagar la electricidad el 17 de julio de 2026 a las 08:00.",
    "proposal": {
      "type": "create_reminder",
      "title": "Pagar la electricidad",
      "due_at": "2026-07-17T08:00:00-04:00",
      "timezone": "America/Caracas"
    },
    "status": "WAITING_CONFIRMATION"
  }
}
```

## `GET /chat/conversations`

Lista conversaciones paginadas del workspace.

## `GET /chat/conversations/{id}`

Devuelve mensajes con paginación. Las partes sensibles deben respetar la política de retención.

## `POST /chat/operations/{id}/confirm`

Confirma una propuesta. La API debe volver a validar permisos, fechas y disponibilidad antes de ejecutar.

## `POST /chat/operations/{id}/cancel`

Cancela una propuesta o job si todavía es cancelable.

---

# 11. Endpoints de memoria

## `POST /memory/nodes`

Crea un nodo explícito.

```json
{
  "type": "preference",
  "label": "Horario preferido de reuniones",
  "content": "Prefiero reuniones después de las 16:00",
  "sensitivity": "personal",
  "provenance": "explicit_user_input"
}
```

## `GET /memory/nodes/{id}`

Devuelve nodo, procedencia y relaciones autorizadas.

## `PATCH /memory/nodes/{id}`

Permite corregir contenido, label, tipo, sensibilidad o expiración. Toda modificación crea un evento de auditoría.

## `DELETE /memory/nodes/{id}`

Debe aplicar política de borrado:

- Marcar como eliminado.
- Eliminar relaciones dependientes.
- Invalidar índices.
- Programar borrado de embeddings y archivos relacionados.
- Confirmar al usuario qué fue eliminado.

## `GET /memory/search`

Parámetros:

```text
q
mode=text|semantic|hybrid|graph
limit
cursor
type
sensitivity
created_after
created_before
```

La respuesta debe incluir relevancia, fuente y nivel de confianza.

## `POST /memory/edges`

Crea relación entre nodos. Las aristas inferidas deben marcarse como `inferred` y no como `explicit`.

## `DELETE /memory/edges/{id}`

Elimina o invalida una relación.

---

# 12. Endpoints del grafo

## `GET /graph/subgraph`

Entrada:

```text
root_node_id
max_depth=2
max_nodes=50
relation_types[]=RELATED_TO
```

Respuesta:

```json
{
  "data": {
    "nodes": [],
    "edges": [],
    "truncated": false,
    "query": {
      "root": "node_123",
      "depth": 2
    }
  }
}
```

## `GET /graph/stats`

Devuelve contadores agregados del workspace:

- Total de nodos.
- Total de relaciones.
- Tipos.
- Memorias expiradas.
- Índices pendientes.

## `POST /graph/rebuild`

Solo para administración o usuario autorizado. Encola reindexación; no bloquea la API.

## `POST /graph/merge`

Fusiona entidades duplicadas con confirmación. Debe conservar procedencia e historial.

---

# 13. Endpoints de recordatorios

## `POST /reminders`

Crea un recordatorio con una regla explícita.

```json
{
  "title": "Revisar presupuesto",
  "description": "Comprobar gastos de la semana",
  "due_at": "2026-07-20T09:00:00-04:00",
  "timezone": "America/Caracas",
  "recurrence": {
    "frequency": "weekly",
    "by_weekday": ["MO"]
  },
  "priority": "normal",
  "channel": "push"
}
```

## `GET /reminders`

Filtros:

```text
status
from
to
priority
channel
cursor
limit
```

## `GET /reminders/{id}`

Incluye regla, próxima ocurrencia, historial y estado.

## `PATCH /reminders/{id}`

Toda modificación debe actualizar futuras ocurrencias sin alterar entregas históricas.

## `POST /reminders/{id}/complete`

Completa la ocurrencia actual o el recordatorio completo según el payload.

## `POST /reminders/{id}/snooze`

Entrada:

```json
{
  "until": "2026-07-17T18:00:00-04:00"
}
```

## `POST /reminders/{id}/cancel`

Cancela futuras ocurrencias y conserva historial.

## `GET /reminders/{id}/deliveries`

Muestra intentos y resultados sin incluir credenciales ni contenido innecesario.

---

# 14. Motor de recordatorios

## 14.1. Separación entre regla y ocurrencia

Un recordatorio recurrente no debe duplicarse como cientos de filas sin control.

```text
Reminder
  └── Recurrence Rule
        ├── Occurrence 2026-07-20
        ├── Occurrence 2026-07-27
        └── Occurrence 2026-08-03
```

Las ocurrencias pueden crearse con una ventana anticipada, por ejemplo 30 días, y generarse progresivamente.

## 14.2. Scheduler

Cada ciclo:

1. Busca recordatorios activos.
2. Calcula ocurrencias próximas según timezone.
3. Adquiere lock.
4. Crea job idempotente.
5. Libera lock.

## 14.3. Delivery worker

1. Toma job.
2. Comprueba que la ocurrencia sigue activa.
3. Comprueba que no fue entregada.
4. Comprueba ventana de silencio.
5. Selecciona canal.
6. Envía notificación.
7. Registra resultado.
8. Reintenta si el error es temporal.

## 14.4. Canales

Cada canal implementa una interfaz:

```python
class NotificationChannel(Protocol):
    async def send(self, notification: Notification) -> DeliveryResult: ...
    async def healthcheck(self) -> HealthStatus: ...
```

---

# 15. Jobs y cola

## 15.1. Tipos de job

```text
transcribe_audio
extract_document
embed_memory
index_memory
consolidate_memory
send_reminder
send_notification
sync_mcp
sync_calendar
generate_briefing
create_backup
restore_backup
purge_expired_data
rebuild_graph
```

## 15.2. Estructura

```json
{
  "id": "job_123",
  "type": "send_reminder",
  "payload_ref": "reminder_occurrence_123",
  "workspace_id": "ws_123",
  "priority": "normal",
  "attempt": 1,
  "max_attempts": 5,
  "status": "running",
  "idempotency_key": "occurrence_123_push",
  "trace_id": "trace_123"
}
```

## 15.3. Prioridades

```text
critical   → operaciones de seguridad o restauración
high       → recordatorios próximos
normal     → transcripción y embeddings
low        → consolidación y estadísticas
```

## 15.4. Dead-letter queue

Un job que supera sus reintentos pasa a DLQ. El usuario o administrador puede:

- Ver el error resumido.
- Reintentar.
- Cancelar.
- Corregir configuración.
- Exportar el incidente.

---

# 16. Audio y archivos

## 16.1. Endpoint de subida

`POST /files/upload` recibe un archivo temporal con:

- Tamaño máximo.
- MIME permitido.
- Hash.
- Usuario/workspace.
- Política de retención.

Nunca se debe confiar solo en la extensión.

## 16.2. Audio

```text
uploaded
→ validated
→ queued_transcription
→ transcribing
→ transcript_ready
→ user_review
→ processed
→ deleted/retained
```

## 16.3. Política de retención

El usuario debe elegir:

- Eliminar audio después de transcribir.
- Conservar audio junto a la memoria.
- Conservar durante un periodo.
- No guardar audio en ningún servidor.

## 16.4. Documentos e imágenes

Los documentos deben procesarse en worker. El OCR o extracción no debe bloquear la request HTTP. La respuesta inicial debe devolver `job_id` y estado.

---

# 17. Agentes, skills y policy engine

## 17.1. Agente

```text
Agent
- id
- workspace_id
- name
- description
- system_prompt
- model_config_json
- autonomy_level
- budget_json
- avatar_id
- status
```

## 17.2. Skill

```text
Skill
- id
- version
- name
- input_schema
- output_schema
- risk_level
- required_tools
- memory_scopes
- confirmation_policy
```

## 17.3. Policy decision

```json
{
  "allowed": false,
  "reason": "TOOL_REQUIRES_CONFIRMATION",
  "risk_level": "high",
  "required_action": "user_confirmation"
}
```

## 17.4. Tool call

Cada llamada debe registrar:

- Agente.
- Skill.
- Herramienta.
- Input filtrado.
- Scope.
- Resultado.
- Duración.
- Error.
- Confirmación.

Los inputs completos pueden omitirse o cifrarse si contienen datos sensibles.

---

# 18. MCP Gateway

## 18.1. Registro

`POST /integrations/mcp`

Entrada:

```json
{
  "name": "graphify-local",
  "transport": "streamable_http",
  "endpoint": "http://localhost:8000/mcp",
  "auth_type": "bearer",
  "scopes": ["graph.read"]
}
```

El token real no debe devolverse después de guardarse.

## 18.2. Handshake

El gateway debe almacenar:

- Protocol version.
- Server name.
- Server version.
- Capabilities.
- Tools.
- Resources.
- Fecha de último healthcheck.

## 18.3. Scopes iniciales

```text
graph.read
graph.write
memory.read
memory.write
calendar.read
calendar.write
email.read
email.draft
email.send
filesystem.read
filesystem.write
web.fetch
```

`email.send`, `filesystem.write` y acciones equivalentes requieren confirmación fuerte y no se habilitan por defecto.

## 18.4. Aislamiento

- Timeouts.
- Límite de tamaño de respuestas.
- Límite de llamadas por operación.
- Red permitida.
- No pasar todos los secretos del proceso a un MCP.
- Credenciales específicas por integración.
- Revocación.

---

# 19. LLM Router y contexto

## 19.1. Pipeline

```text
Intent classifier
  ↓
Context retriever
  ↓
Prompt builder
  ↓
Provider adapter
  ↓
Structured output validator
  ↓
Policy engine
```

## 19.2. Contexto mínimo

El retriever debe enviar solamente:

- Memorias relevantes.
- Relaciones necesarias.
- Preferencias aplicables.
- Estado de tarea relacionado.
- Instrucciones de la skill.

No se debe enviar el grafo completo ni todo el historial de conversación por defecto.

## 19.3. Structured output

Las salidas deben validarse con JSON Schema/Pydantic.

```json
{
  "intent": "create_reminder",
  "confidence": 0.96,
  "fields": {
    "title": "Pagar la electricidad",
    "due_at": "2026-07-17T08:00:00-04:00"
  },
  "needs_clarification": false
}
```

Una respuesta que no valida no puede pasar al ejecutor.

---

# 20. Persistencia y repositorios

## 20.1. Repositories

Interfaces esperadas:

```python
class MemoryRepository(Protocol):
    async def create(self, node: MemoryNode) -> MemoryNode: ...
    async def get(self, node_id: str) -> MemoryNode | None: ...
    async def search(self, query: MemoryQuery) -> list[MemoryNode]: ...
    async def delete(self, node_id: str) -> None: ...
```

## 20.2. Transacciones

Las operaciones que creen un recordatorio y su primera ocurrencia deben ser transaccionales. Las operaciones asíncronas posteriores pueden ser jobs independientes.

## 20.3. Soft delete

Para memorias y relaciones se recomienda soft delete inicial para permitir:

- Auditoría.
- Recuperación limitada.
- Propagación a índices.
- Confirmación de borrado.

Después del periodo definido, un job de purga elimina definitivamente el contenido.

## 20.4. Migraciones

- Alembic.
- Migraciones reversibles cuando sea posible.
- Backup antes de cambios destructivos.
- Versionado de schema.
- No cambiar tablas manualmente en producción.

---

# 21. Caching e índices

## 21.1. Redis

Usos:

- Rate limit.
- Locks.
- Cola.
- Cache de consultas cortas.
- Estado temporal de confirmaciones.
- Pub/sub para actualización de UI.

No usar Redis como única fuente de verdad para memorias o recordatorios.

## 21.2. Índices de base de datos

Índices recomendados:

```text
memory_nodes(workspace_id, type)
memory_nodes(workspace_id, created_at)
memory_nodes(workspace_id, sensitivity)
reminders(workspace_id, status, next_due_at)
occurrences(status, due_at)
jobs(status, priority, created_at)
execution_logs(workspace_id, created_at)
```

## 21.3. Índice vectorial

El vector debe asociarse al workspace y al nodo. Si el nodo se elimina, su vector debe invalidarse y purgarse.

---

# 22. Notificaciones

## 22.1. Modelo

```text
Notification
- id
- workspace_id
- occurrence_id nullable
- channel
- payload_ref
- status
- attempts
- delivered_at
- last_error
```

## 22.2. Estados

```text
pending
sending
delivered
failed
cancelled
```

## 22.3. Reglas

- No incluir secretos en previews de notificación.
- Permitir modo silencioso.
- Respetar preferencias de canal.
- No enviar una notificación duplicada por reintento.
- Mostrar error de configuración sin fingir entrega.

---

# 23. Exportación, importación y backups

## 23.1. Exportación

`POST /exports`

Debe ser asíncrona para volúmenes grandes.

Contenido:

```text
manifest.json
user-settings.json
memories.jsonl.enc
edges.jsonl.enc
reminders.jsonl.enc
agents.jsonl.enc
files/
checksums.sha256
```

## 23.2. Importación

Debe:

- Validar schema.
- Verificar checksum.
- Mostrar resumen antes de importar.
- Permitir importar a workspace nuevo.
- Detectar duplicados.
- Mantener procedencia de importación.

## 23.3. Backup

- Backup lógico cifrado.
- Backup de base de datos según despliegue.
- Backup de objetos.
- Prueba periódica de restauración.
- No guardar la clave de descifrado junto al backup.

---

# 24. Healthchecks

## `GET /health/live`

Responde si el proceso está vivo.

```json
{
  "status": "ok",
  "service": "vnbot-api",
  "version": "0.1.0"
}
```

## `GET /health/ready`

Comprueba dependencias críticas:

- Base de datos.
- Migraciones.
- Cola cuando el modo lo requiere.
- Storage si se necesitan archivos.

## `GET /health/dependencies`

Devuelve:

```json
{
  "database": {"status": "ok", "latency_ms": 4},
  "redis": {"status": "ok", "latency_ms": 2},
  "storage": {"status": "ok"},
  "ollama": {"status": "optional_unavailable"},
  "mcp_gateway": {"status": "ok"}
}
```

Los proveedores opcionales no deben hacer que una instalación básica aparezca como completamente caída.

---

# 25. Errores y códigos

## 25.1. Categorías

```text
AUTH_*          autenticación
PERMISSION_*    autorización
VALIDATION_*    payload inválido
MEMORY_*        memoria/grafo
REMINDER_*      recordatorios
JOB_*           trabajos
LLM_*           proveedores IA
MCP_*           herramientas MCP
FILE_*          archivos
INTEGRATION_*   integraciones
SYSTEM_*        infraestructura
```

## 25.2. Ejemplos

```text
AUTH_SESSION_EXPIRED
PERMISSION_TOOL_DENIED
VALIDATION_INVALID_DATETIME
REMINDER_AMBIGUOUS_TIME
REMINDER_ALREADY_COMPLETED
JOB_MAX_RETRIES
LLM_PROVIDER_RATE_LIMIT
MCP_TOOL_TIMEOUT
MCP_SCOPE_REQUIRED
FILE_TOO_LARGE
INTEGRATION_REAUTH_REQUIRED
SYSTEM_DATABASE_UNAVAILABLE
```

## 25.3. Retryable

Cada error debe indicar si es reintentable. No reintentar automáticamente errores de autorización, validación o confirmación faltante.

---

# 26. Seguridad del backend

## 26.1. Secretos

- Variables de entorno solo en desarrollo controlado.
- Docker secrets o vault en servidor.
- Keychain del sistema para desktop.
- No tokens en URL.
- No secretos en logs.
- Rotación documentada.

## 26.2. Archivos

- Validar tamaño.
- Validar MIME real.
- Renombrar con identificadores internos.
- Guardar fuera del web root.
- Analizar malware cuando el despliegue lo requiera.
- Impedir path traversal.

## 26.3. URLs externas

El fetch web y MCP deben protegerse contra SSRF:

- Bloquear redes privadas por defecto.
- Permitir allowlist configurada.
- Resolver y verificar IP final.
- Limitar redirects.
- Timeout.
- Tamaño máximo de respuesta.

## 26.4. Prompt injection

El contenido de emails, páginas, documentos y MCP debe tratarse como datos no confiables. Las instrucciones encontradas dentro de esos datos no deben modificar la política del agente.

---

# 27. Concurrencia y consistencia

## 27.1. Recordatorios

Usar lock por ocurrencia. La entrega debe ser exactamente una vez en condiciones normales y como máximo una vez en escenarios de recuperación no verificable, con deduplicación por provider cuando sea posible.

## 27.2. Memoria

Usar versionado optimista:

```text
PATCH con expected_version
```

Si otro proceso modificó el nodo, devolver conflicto y no sobrescribir silenciosamente.

## 27.3. Integraciones

Cada integración debe guardar cursor o timestamp de sincronización y manejar eventos repetidos.

---

# 28. Escalabilidad

## 28.1. Escalado vertical inicial

Para una instalación personal, aumentar CPU/RAM y mantener una sola instancia puede ser suficiente.

## 28.2. Escalado horizontal

La API debe ser stateless salvo por:

- Sesión server-side si se usa.
- Cache Redis.
- Base de datos.
- Storage externo.

Los workers pueden aumentar según la cola.

## 28.3. Cuellos de botella esperados

- Transcripción local.
- Embeddings.
- Proveedores LLM.
- Reindexación.
- Render del grafo en cliente.
- Entrega de notificaciones.
- Storage de audios.

## 28.4. Límites configurables

- Memorias por workspace.
- Tamaño de archivo.
- Audio diario.
- Jobs concurrentes.
- Tokens por usuario.
- Profundidad de grafo.
- Número de MCP.
- Herramientas por agente.

---

# 29. Configuración

## 29.1. Variables principales

```env
VNBOT_ENV=production
VNBOT_BASE_URL=https://vnbot.example.com
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
STORAGE_ENDPOINT=http://minio:9000
STORAGE_BUCKET=vnbot
SESSION_SECRET=...
ENCRYPTION_KEY=...
DEFAULT_TIMEZONE=UTC
LOG_LEVEL=INFO
```

## 29.2. Reglas

- `.env.example` no contiene secretos reales.
- Configuración crítica debe validarse al iniciar.
- Proveedores opcionales pueden quedar desactivados.
- Un error de configuración debe indicar cómo corregirse.

---

# 30. Pruebas del backend

## 30.1. Unitarias

- Entidades.
- Recurrencia.
- Timezones.
- Policy engine.
- Idempotency keys.
- Parsers.
- Validación de tools.
- Cifrado.

## 30.2. Integración

- SQLite.
- PostgreSQL.
- Redis.
- Worker.
- Scheduler.
- Mock LLM.
- Mock MCP.
- Storage.

## 30.3. Contratos

- OpenAPI.
- JSON Schema de skills.
- Tool schemas MCP.
- Export/import.
- Eventos internos.

## 30.4. E2E

- Crear recordatorio y reiniciar worker.
- Reintentar delivery.
- Confirmar acción.
- Cancelar antes de ejecución.
- Borrar memoria y verificar índices.
- Desconectar MCP.
- Importar backup.

---

# 31. Observabilidad y privacidad

La observabilidad debe ayudar a operar el sistema sin convertir el contenido del usuario en telemetría.

## Se puede registrar

- IDs internos.
- Tiempos.
- Estados.
- Códigos de error.
- Proveedor/modelo.
- Tokens agregados.
- Tamaños.
- Conteos.
- Hashes no reversibles cuando sean necesarios.

## No registrar por defecto

- Plaintext de memorias.
- Audio.
- API keys.
- Tokens OAuth.
- Passwords.
- Contenido completo de emails.
- Respuestas completas de proveedores.

---

# 32. Requisitos para Docker

## API

- Imagen no root.
- Healthcheck HTTP.
- Migración explícita.
- Puerto interno.
- Sin persistencia local crítica.

## Worker

- Healthcheck de proceso.
- Conexión a Redis.
- Conexión a base de datos.
- Graceful shutdown.
- Visibilidad de jobs activos.

## Scheduler

- Lock distribuido.
- Una sola autoridad para crear ocurrencias.
- Graceful shutdown.

## Volúmenes

```text
postgres_data
redis_data opcional
minio_data
vnbot_backups
```

---

# 33. Criterios de aceptación backend MVP

El backend cumple el MVP cuando:

1. Puede crear y consultar una memoria.
2. Puede crear un nodo y una relación.
3. Puede crear un recordatorio con zona horaria.
4. Puede generar ocurrencias recurrentes.
5. Puede entregar una notificación sin duplicarla.
6. Puede reintentar un job fallido.
7. Puede detener un job cancelable.
8. Puede procesar una instrucción sin LLM mediante heurística.
9. Puede registrar una operación y su auditoría.
10. Puede exportar/importar datos.
11. Puede ejecutarse con SQLite en local.
12. Puede ejecutarse con PostgreSQL y Redis en servidor.
13. Expone live/ready/dependencies.
14. No mezcla credenciales con datos de usuario.
15. No autoriza herramientas solo porque el LLM las solicite.

---

# 34. Orden de implementación backend

## Fase 1 — Dominio

- Entidades.
- Estados.
- Reglas de recordatorio.
- Memoria y grafo.
- Tests unitarios.

## Fase 2 — Persistencia

- SQLAlchemy.
- SQLite.
- Migraciones.
- Repositorios.
- Exportación básica.

## Fase 3 — API

- Auth.
- Memory.
- Graph.
- Reminders.
- Operations.
- Health.

## Fase 4 — Jobs

- Tabla/cola.
- Worker.
- Scheduler.
- Locks.
- Reintentos.
- Delivery.

## Fase 5 — IA

- Heurística.
- LLM Router.
- Structured output.
- Embeddings.

## Fase 6 — Integraciones

- Notificaciones.
- MCP interno.
- MCP externo.
- Graphify.
- Calendario.

## Fase 7 — Producción

- PostgreSQL.
- Redis.
- MinIO.
- Docker.
- Observabilidad.
- Backups.
- CI/CD.

---

# 35. Decisiones abiertas

1. Dramatiq o Celery como worker principal.
2. SQLite job queue propia o Redis obligatorio en modo local.
3. `pgvector` como único índice vectorial o adaptador adicional.
4. Transporte WebSocket o SSE para estados de jobs.
5. Duración de retención de operaciones y logs.
6. Política de soft delete por tipo de dato.
7. Soporte de múltiples regiones/zonas horarias en workspaces compartidos.
8. Formato definitivo de plugins externos.
9. Servicio separado de notificaciones en VNBOT 1.0.
10. WebAuthn en el MVP o en una versión posterior.

---

# 36. Conclusión

El backend de VNBOT debe ser una plataforma modular, no un conjunto de endpoints que llaman directamente a un LLM. La memoria, los recordatorios y las operaciones deben tener reglas deterministas y estados persistentes. La IA, MCP y las integraciones deben utilizar esas reglas, no sustituirlas.

La estructura recomendada es:

```text
API stateless
+ dominio explícito
+ storage adapters
+ jobs durables
+ scheduler idempotente
+ LLM Router
+ policy engine
+ MCP Gateway
+ auditoría
+ healthchecks
```

Esta arquitectura permite comenzar con SQLite y una instalación personal, y evolucionar hacia PostgreSQL, Redis, workers replicados y múltiples agentes sin reescribir el núcleo. También permite que VNBOT se distribuya en web, APK, desktop, Docker y CLI manteniendo el mismo modelo de datos y las mismas reglas de seguridad.

---

# 37. Endpoints de sincronización (fase 0.3+)

Estos endpoints se implementan cuando la sync strategy esté diseñada y probada (ver [Estrategia de Sync](./11-ESTRATEGIA-SYNC-VNBOT.md)).

## `GET /api/v1/sync/status`

Devuelve el estado de sincronización del workspace.

## `POST /api/v1/sync/push`

Envía cambios locales al servidor. El cuerpo incluye ops con version vectors.

## `POST /api/v1/sync/pull`

Recibe cambios del servidor desde un cursor dado.

## `GET /api/v1/sync/conflicts`

Lista conflictos pendientes de resolución.

## `POST /api/v1/sync/conflicts/{id}/resolve`

Resuelve un conflicto específico con la opción elegida por el usuario.

## `POST /api/v1/sync/full-reset`

Resetea la sincronización (peligroso, requiere confirmación doble).

---

# 38. Requisitos de testing del backend

## 38.1. Tests unitarios

Cada servicio de dominio debe tener tests unitarios:

- `MemoryService`: crear, actualizar, borrar, buscar, relacionar, olvidar.
- `ReminderService`: crear puntual, crear recurrente, disparar, completar, posponer.
- `GraphService`: agregar nodo, agregar edge, recorrido, invalidación.
- `AgentService`: crear, asignar skills, verificar permisos.
- `PolicyEngine`: evaluar permiso, denegar por defecto, auditar.
- `LLMRouter`: seleccionar provider, fallback, structured output parsing.

Cobertura mínima: 80% en dominio, 70% en API.

## 38.2. Tests de integración

- Crear recordatorio → verificar que se dispara en el momento correcto.
- Crear memoria → verificar que aparece en búsqueda.
- Conectar MCP tool → verificar que se ejecuta con permisos correctos.
- Exportar e importar → verificar integridad de datos.

## 38.3. Contract testing para MCP

Cada tool MCP debe tener un contract test que verifique:
- Input schema es válido.
- Output schema es válido.
- La tool respeta sus scopes declarados.
- Un fallo de la tool no afecta al núcleo.

## 38.4. Benchmarks automatizados

- Operaciones CRUD sobre memorias (1,000 ops).
- Búsqueda textual con 5,000 memorias.
- Recordatorios: crear 1,000 y verificar que ninguno se duplica.
- Grafo: subgrafo profundidad 3 con 50 nodos.
- Scheduler: 100 jobs concurrentes sin duplicados.

Ver [Testing y Observabilidad](./12-TESTING-Y-OBSERVABILIDAD-VNBOT.md) para la estrategia completa.

---

# 39. Instrumentación de observabilidad

Todos los servicios del backend deben estar instrumentados con OpenTelemetry:

## 39.1. Spans obligatorios

- `vnbot.api.<method>.<endpoint>`: cada request HTTP.
- `vnbot.domain.<service>.<operation>`: cada operación de dominio.
- `vnbot.llm.<provider>.call`: cada llamada a LLM.
- `vnbot.mcp.<tool>.call`: cada invocación de tool MCP.
- `vnbot.worker.<job_type>.execute`: cada ejecución de job.
- `vnbot.sync.push` / `vnbot.sync.pull`: cada operación de sincronización.

## 39.2. Métricas obligatorias

- `vnbot_api_requests_total{method, endpoint, status}`
- `vnbot_api_duration_seconds{method, endpoint}` (histogram)
- `vnbot_llm_tokens_total{provider, model, direction}`
- `vnbot_llm_duration_seconds{provider, model}`
- `vnbot_jobs_total{type, status}`
- `vnbot_jobs_duration_seconds{type}`
- `vnbot_sync_conflicts_total{workspace_id}`
- `vnbot_graph_nodes_total{workspace_id}`
- `vnbot_graph_query_duration_seconds{operation}`

## 39.3. Regla de contenido

Ningún span, métrica ni log debe contener el contenido de una memoria, mensaje o dato personal. Solo IDs, estados, duraciones y tipos.

---

# 40. Restricciones de rendimiento del grafo

## 40.1. Límites por consulta

- Profundidad máxima por defecto: 3.
- Top-K máximo configurable: 50 (por defecto 20).
- Nodos máximos devueltos por consulta: 100.
- Timeout por consulta: 5 segundos.

## 40.2. No cargar el grafo completo

El cliente nunca recibe el grafo completo. Todas las consultas son server-side con paginación y filtros. La visualización recibe solo los nodos y edges del resultado.

## 40.3. Degradación graciosa

Si una consulta excede los límites, el sistema:
1. Reduce la profundidad.
2. Aplica top-K más agresivo.
3. Devuelve un mensaje al usuario: "La consulta es muy amplia. Refina los filtros o selecciona un nodo de inicio."
4. Nunca agota la memoria del servidor por una consulta de grafo.
