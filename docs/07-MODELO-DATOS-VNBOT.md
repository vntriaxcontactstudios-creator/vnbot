# VNBOT — Modelo de Datos

> **Documento:** Modelo de datos y persistencia
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Diseño de entidades y relaciones
> **Fecha:** 2026-07-16
> **Documentos relacionados:** [PRD](./01-PRD-VNBOT.md), [TRD](./02-TRD-VNBOT.md), [Esquema Backend](./03-ESQUEMA-BACKEND-VNBOT.md), [Seguridad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md)

---

# 1. Propósito

Este documento define las entidades, relaciones, identificadores, estados, reglas de integridad y formatos de persistencia de VNBOT.

El modelo debe soportar:

- Instalación local con SQLite.
- PWA con IndexedDB.
- Servidor con PostgreSQL.
- Memoria de nodos y relaciones.
- Recordatorios puntuales y recurrentes.
- Agentes y skills.
- Integraciones MCP.
- Jobs asíncronos.
- Archivos y audio.
- Auditoría.
- Exportación/importación.
- Sincronización futura entre dispositivos.

El modelo no debe asumir que todo el contenido estará en texto plano. Algunos campos se almacenarán cifrados, algunos serán metadatos operativos y otros serán índices derivados.

---

# 2. Principios del modelo

## 2.1. Aislamiento por workspace

Toda entidad relacionada con datos del usuario debe tener un `workspace_id` directo o heredado de una relación autorizada.

## 2.2. Procedencia obligatoria

Toda memoria o relación generada por IA debe indicar cómo fue creada:

```text
explicit_user_input
user_confirmed
conversation_extraction
audio_transcription
image_ocr
llm_inference
external_integration
imported_data
system_generated
```

## 2.3. Confianza y autoridad son diferentes

- `confidence`: qué tan seguro está el sistema de su interpretación.
- `authority`: si el usuario confirmó el dato.

Una inferencia con confianza 0.98 no equivale a una preferencia confirmada.

## 2.4. Borrado gradual

Los datos pueden pasar por:

```text
active → deleted/soft_deleted → purged
```

La purga definitiva debe incluir índices, vectores, archivos, cache y referencias derivadas.

## 2.5. Fechas en UTC y zona explícita

Los timestamps técnicos se guardan en UTC. Las operaciones de usuario también deben conservar la zona horaria de interpretación.

## 2.6. Identificadores opacos

No usar emails, nombres o índices secuenciales como IDs públicos. Usar UUID/ULID o identificadores equivalentes.

---

# 3. Capas de almacenamiento

## 3.1. Datos de dominio

Fuente de verdad:

- Usuarios.
- Workspaces.
- Memorias.
- Relaciones.
- Recordatorios.
- Agentes.
- Integraciones.
- Jobs.

## 3.2. Datos derivados

Pueden reconstruirse:

- Embeddings.
- Índices de búsqueda.
- Resúmenes.
- Estadísticas.
- Layout del grafo.
- Cache.

## 3.3. Archivos

Se almacenan fuera de la tabla principal:

- Audio.
- Imágenes.
- Documentos.
- Backups.
- Assets generados.

La base de datos conserva una referencia segura y metadata.

## 3.4. Adaptadores

```text
IndexedDBAdapter → PWA
SQLiteAdapter    → local/desktop
PostgresAdapter  → server
FileAdapter      → export/import
ObjectStorage    → S3/MinIO/filesystem
```

---

# 4. Convenciones

## 4.1. IDs

Formato recomendado:

```text
usr_01J...
ws_01J...
mem_01J...
edge_01J...
rem_01J...
occ_01J...
job_01J...
```

La parte legible ayuda a debugging, pero no debe revelar información personal.

## 4.2. Timestamps

Campos estándar:

```text
created_at
updated_at
deleted_at
expires_at
```

Todos en UTC ISO 8601 o tipo timestamp con zona en la base de datos.

## 4.3. JSON metadata

Usar JSON para campos extensibles, pero no ocultar en JSON campos necesarios para filtrar, autorizar o indexar.

Correcto:

```text
sensitivity como columna
provider_name como columna
metadata adicional en JSON
```

## 4.4. Versiones

Cada registro mutable importante puede tener:

- `version` entero.
- `schema_version` para exportaciones.
- `source_version` para integraciones.

---

# 5. Entidad User

Representa la identidad dentro de una instalación con autenticación.

```text
User
- id: string PK
- email: string nullable, unique cuando exista
- display_name: string nullable
- password_hash: string nullable
- status: active|locked|pending|deleted
- timezone: IANA timezone
- locale: string
- created_at: timestamp
- updated_at: timestamp
- last_login_at: timestamp nullable
```

## Reglas

- No almacenar contraseña en texto.
- `email` puede ser nullable en modo local.
- No usar email como ID.
- La eliminación de usuario debe revocar sesiones e integraciones.
- Las memorias pertenecen a workspaces, no directamente a emails.

---

# 6. Sesiones y seguridad de identidad

## Session

```text
Session
- id
- user_id
- device_id nullable
- refresh_token_hash
- created_at
- expires_at
- revoked_at nullable
- last_seen_at
- ip_hash nullable
- user_agent_hash nullable
```

Nunca almacenar refresh tokens en texto plano.

## Device

```text
Device
- id
- user_id
- name
- platform: web|android|desktop|cli
- public_key nullable
- last_sync_at nullable
- last_seen_at
- created_at
- revoked_at nullable
```

El dispositivo puede tener una clave pública para futuras funciones de sincronización y aprobación local.

## TwoFactorCredential futuro

```text
TwoFactorCredential
- id
- user_id
- type: totp|webauthn
- secret_encrypted
- label
- created_at
- last_used_at
- revoked_at
```

---

# 7. Workspace

Un workspace es el límite de datos, memoria y permisos.

```text
Workspace
- id
- owner_user_id
- name
- type: personal|family|team|project
- status: active|archived|deleted
- default_timezone
- settings_json
- created_at
- updated_at
```

## WorkspaceMember

```text
WorkspaceMember
- workspace_id
- user_id
- role: owner|admin|member|viewer
- status: active|invited|suspended|removed
- invited_at
- joined_at nullable
- created_at
```

## Reglas

- Un usuario puede pertenecer a varios workspaces.
- Un recurso no puede cruzar workspaces sin una operación explícita.
- Un agente debe pertenecer a un workspace.
- Las integraciones deben estar vinculadas a un workspace concreto.

---

# 8. Conversation y Message

## Conversation

```text
Conversation
- id
- workspace_id
- user_id
- agent_id nullable
- title nullable
- status: active|archived|deleted
- created_at
- updated_at
- last_message_at
```

## Message

```text
Message
- id
- conversation_id
- workspace_id
- role: user|assistant|system|tool
- content_ciphertext nullable
- content_preview nullable
- content_format: text|markdown|json|audio_transcript
- model_provider nullable
- model_name nullable
- operation_id nullable
- source_file_id nullable
- created_at
- deleted_at nullable
```

## Reglas

- El contenido puede estar cifrado.
- `content_preview` debe ser opcional y no contener secretos.
- Los mensajes de herramientas deben referenciar la ejecución, no copiar credenciales.
- La retención de conversación debe ser configurable.

---

# 9. MemoryNode

Es la entidad principal de memoria personal.

```text
MemoryNode
- id
- workspace_id
- type
- label
- content_ciphertext
- content_format
- structured_data_ciphertext nullable
- source_type
- source_id nullable
- provenance
- authority
- confidence decimal
- sensitivity
- status: active|superseded|deleted|expired|archived
- valid_from nullable
- valid_until nullable
- expires_at nullable
- version integer
- created_by_user_id nullable
- created_by_agent_id nullable
- created_at
- updated_at
- deleted_at nullable
```

## Tipos

```text
person
place
project
task
reminder
event
preference
note
document
conversation
agent
contact
secret_reference
```

## `authority`

```text
explicit
user_confirmed
system_extracted
inferred
external_source
```

## `sensitivity`

```text
public
personal
sensitive
secret
```

## Reglas

- No devolver `content_ciphertext` como texto a clientes sin autorización.
- `secret_reference` no debe contener contraseñas directamente.
- Una memoria inferida debe poder solicitar confirmación.
- Una memoria sustituida conserva referencia histórica, salvo purga.

---

# 10. MemoryEdge

Representa una relación entre dos nodos.

```text
MemoryEdge
- id
- workspace_id
- source_node_id
- target_node_id
- relation_type
- properties_ciphertext nullable
- provenance
- authority
- confidence decimal
- status: active|invalidated|superseded|deleted
- valid_from nullable
- valid_until nullable
- version integer
- created_by_user_id nullable
- created_by_agent_id nullable
- created_at
- updated_at
- deleted_at nullable
```

## Relaciones iniciales

```text
KNOWS
WORKS_ON
RELATED_TO
DEPENDS_ON
REMINDER_FOR
HAPPENS_AT
PREFERS
SUPERSEDES
CONTRADICTS
DERIVED_FROM
ASSIGNED_TO
MENTIONED_IN
LOCATED_AT
```

## Reglas

- `source_node_id` y `target_node_id` deben pertenecer al mismo workspace.
- No crear auto-relaciones salvo tipos explícitos.
- Las aristas inferidas deben indicar origen.
- Al eliminar un nodo, sus aristas se invalidan o se purgan según política.

---

# 11. MemorySource y Provenance

Una memoria debe poder explicar de dónde provino.

```text
MemorySource
- id
- workspace_id
- source_type: message|audio|image|document|integration|manual|import
- source_id
- provider_name nullable
- provider_model nullable
- excerpt_ciphertext nullable
- created_at
```

## Ejemplo

```json
{
  "provenance": "conversation_extraction",
  "source_type": "message",
  "source_id": "msg_123",
  "authority": "system_extracted",
  "confidence": 0.86
}
```

La UI debe poder mostrar una explicación comprensible sin revelar un documento completo innecesariamente.

---

# 12. MemoryVersion

Permite conservar cambios y resolver conflictos.

```text
MemoryVersion
- id
- memory_node_id
- version
- content_ciphertext
- structured_data_ciphertext nullable
- changed_by_user_id nullable
- changed_by_agent_id nullable
- change_reason
- created_at
```

## Motivos

```text
created
user_edit
agent_update
contradiction_resolution
imported
system_cleanup
```

---

# 13. EmbeddingIndex

Los embeddings son datos derivados y deben poder regenerarse.

```text
EmbeddingIndex
- id
- workspace_id
- entity_type: memory_node|message|document
- entity_id
- model_name
- dimensions
- vector_reference nullable
- content_hmac
- status: pending|ready|stale|deleted|failed
- created_at
- updated_at
```

## Reglas

- No crear embeddings remotos sin consentimiento.
- El vector debe estar limitado al workspace.
- Si se borra el contenido, se borra o invalida el embedding.
- Si cambia el modelo, se puede reindexar sin cambiar la memoria original.

---

# 14. Reminder

Representa la intención recurrente o puntual del usuario.

```text
Reminder
- id
- workspace_id
- created_by_user_id
- created_by_agent_id nullable
- title
- description_ciphertext nullable
- timezone
- recurrence_rule nullable
- priority: low|normal|high|critical
- channel
- recipient_ref nullable
- status: active|paused|completed|cancelled|expired
- source_memory_id nullable
- next_due_at nullable
- created_at
- updated_at
- completed_at nullable
- cancelled_at nullable
```

## Reglas

- Un recordatorio recurrente no se representa con una cantidad infinita de filas.
- `next_due_at` es un índice de conveniencia; la regla es la fuente de verdad.
- `recipient_ref` no debe almacenar información excesiva de terceros.
- Recordatorios externos requieren política de consentimiento.

---

# 15. ReminderOccurrence

Representa una instancia ejecutable del recordatorio.

```text
ReminderOccurrence
- id
- reminder_id
- workspace_id
- occurrence_key unique
- due_at
- timezone
- status: pending|queued|sending|delivered|snoozed|completed|failed|cancelled
- attempts
- delivered_at nullable
- completed_at nullable
- snoozed_until nullable
- last_error_code nullable
- created_at
- updated_at
```

## `occurrence_key`

Debe ser determinista para impedir duplicados:

```text
{reminder_id}:{due_at_utc}:{rule_version}
```

---

# 16. Notification y Delivery

## Notification

```text
Notification
- id
- workspace_id
- occurrence_id nullable
- channel: web_push|desktop|android|email|telegram|whatsapp
- title
- body_ciphertext nullable
- status: pending|sending|delivered|failed|cancelled
- priority
- created_at
- sent_at nullable
```

## DeliveryAttempt

```text
DeliveryAttempt
- id
- notification_id
- attempt_number
- provider_message_id nullable
- status
- error_code nullable
- response_metadata_json
- created_at
```

No guardar respuesta completa de un proveedor si contiene datos innecesarios o secretos.

---

# 17. Listas y elementos

## List

```text
List
- id
- workspace_id
- name
- description_ciphertext nullable
- status: active|archived|deleted
- created_by_user_id
- created_at
- updated_at
```

## ListItem

```text
ListItem
- id
- list_id
- title_ciphertext
- position
- status: pending|completed|cancelled
- priority
- due_at nullable
- source_memory_id nullable
- created_at
- updated_at
- completed_at nullable
```

La posición puede representarse con un campo decimal o un sistema de ordenación que evite reescribir toda la lista en cada movimiento.

---

# 18. Agent

```text
Agent
- id
- workspace_id
- name
- description
- avatar_id
- system_prompt_ciphertext
- model_provider
- model_name
- model_config_json
- autonomy_level
- budget_json
- status: draft|active|paused|archived
- created_by_user_id
- created_at
- updated_at
```

## `autonomy_level`

```text
0: answer_only
1: propose
2: internal_actions
3: external_confirmed
4: bounded_automation
```

## Reglas

- El agente no recibe todas las memorias por defecto.
- Las herramientas se asignan mediante permisos separados.
- El prompt puede estar cifrado.
- Cambios de autonomía deben crear auditoría.

---

# 19. Skill

```text
Skill
- id
- source
- name
- version
- description
- manifest_json
- instructions_ciphertext nullable
- license
- risk_level
- signature nullable
- status: available|installed|disabled|revoked
- created_at
- updated_at
```

## AgentSkill

```text
AgentSkill
- agent_id
- skill_id
- enabled
- config_json
- installed_at
- updated_at
```

## Manifest mínimo

```yaml
id: reminder.create
version: 1.0.0
risk_level: low
required_tools:
  - reminder_create
memory_scopes:
  - personal
confirmation: required_if_ambiguous
input_schema: schemas/reminder-input.json
output_schema: schemas/reminder-output.json
```

---

# 20. ToolPermission

```text
ToolPermission
- id
- workspace_id
- agent_id
- integration_id nullable
- tool_name
- permission_level: deny|read|write|execute
- scope_json
- requires_confirmation
- max_calls_per_operation nullable
- created_by_user_id
- created_at
- revoked_at nullable
```

## Reglas

- Deny por defecto.
- Una skill no puede ampliar permisos por sí sola.
- Un agente no puede usar una herramienta sin permiso vigente.
- La revocación debe ser inmediata para nuevas llamadas.

---

# 21. Integration

```text
Integration
- id
- workspace_id
- type: mcp|calendar|email|telegram|whatsapp|storage
- name
- provider
- status: disconnected|connecting|healthy|degraded|reauth_required|revoked
- transport nullable
- endpoint_encrypted nullable
- credentials_ref nullable
- scopes_json
- capabilities_json
- last_healthcheck_at nullable
- created_at
- updated_at
```

## CredentialsRef

Las credenciales reales deben vivir en un secret store o campo cifrado separado.

```text
CredentialRef
- id
- integration_id
- encrypted_secret
- key_version
- expires_at nullable
- rotated_at nullable
- revoked_at nullable
```

Nunca devolver `encrypted_secret` a la aplicación web una vez almacenado.

---

# 22. MCPServer y MCPTool

## MCPServer

```text
MCPServer
- id
- integration_id
- protocol_version
- server_name
- server_version
- capabilities_json
- last_initialize_at
- status
```

## MCPTool

```text
MCPTool
- id
- mcp_server_id
- name
- description
- input_schema_json
- output_schema_json nullable
- risk_level
- enabled
- discovered_at
```

Las herramientas descubiertas deben quedar deshabilitadas hasta que el usuario o una política las habilite.

---

# 23. Operation y ExecutionLog

## Operation

```text
Operation
- id
- workspace_id
- user_id
- agent_id nullable
- conversation_id nullable
- type
- status
- risk_level
- input_ref
- proposal_json nullable
- requires_confirmation
- confirmed_at nullable
- created_at
- expires_at nullable
- completed_at nullable
```

## ExecutionLog

```text
ExecutionLog
- id
- workspace_id
- operation_id
- agent_id nullable
- integration_id nullable
- tool_name nullable
- status
- duration_ms nullable
- error_code nullable
- input_hash nullable
- result_summary_ciphertext nullable
- created_at
```

El log debe ser útil sin conservar contenido completo de la memoria o las credenciales.

---

# 24. Job

```text
Job
- id
- workspace_id
- type
- payload_ref
- status: pending|running|retrying|succeeded|failed|cancelled|dead_letter
- priority
- idempotency_key
- attempt
- max_attempts
- available_at
- started_at nullable
- finished_at nullable
- last_error_code nullable
- trace_id
- created_at
```

## Tipos

```text
transcribe_audio
extract_document
embed_memory
index_memory
send_reminder
send_notification
sync_mcp
generate_briefing
create_backup
restore_backup
purge_data
rebuild_graph
```

---

# 25. AudioAsset, FileAsset y Document

## FileAsset

```text
FileAsset
- id
- workspace_id
- owner_user_id
- storage_key
- original_name_ciphertext nullable
- mime_type
- size_bytes
- sha256
- sensitivity
- retention_policy
- status: uploaded|processing|ready|failed|deleted
- created_at
- expires_at nullable
- deleted_at nullable
```

## AudioAsset

```text
AudioAsset
- file_asset_id
- duration_ms
- sample_rate nullable
- transcription_status
- transcript_node_id nullable
- transcription_provider nullable
- delete_after_transcription
```

## Document

```text
Document
- file_asset_id
- title_ciphertext nullable
- extraction_status
- extracted_text_node_id nullable
- page_count nullable
- ocr_provider nullable
```

---

# 26. ExportJob e ImportJob

## ExportJob

```text
ExportJob
- id
- workspace_id
- requested_by_user_id
- scope_json
- include_files
- include_audio
- encryption_mode
- status
- file_asset_id nullable
- expires_at
- created_at
- completed_at nullable
```

## ImportJob

```text
ImportJob
- id
- workspace_id
- requested_by_user_id
- source_file_id
- source_schema_version
- conflict_policy
- status
- summary_json nullable
- created_at
- completed_at nullable
```

---

# 27. SyncOutbox y SyncCursor

Para sincronización futura:

## SyncOutbox

```text
SyncOutbox
- id
- device_id
- workspace_id
- entity_type
- entity_id
- operation: create|update|delete
- payload_ciphertext
- version
- status: pending|sent|acknowledged|conflict|failed
- idempotency_key
- created_at
```

## SyncCursor

```text
SyncCursor
- device_id
- workspace_id
- server_cursor
- last_sync_at
- status
```

La sincronización no debe considerarse completa solo porque el cliente envió datos; debe existir confirmación del servidor.

---

# 28. Relaciones principales

```text
User 1 ─── N WorkspaceMember
Workspace 1 ─── N MemoryNode
Workspace 1 ─── N MemoryEdge
MemoryNode N ─── N MemoryNode vía MemoryEdge
Workspace 1 ─── N Reminder
Reminder 1 ─── N ReminderOccurrence
ReminderOccurrence 1 ─── N Notification
Notification 1 ─── N DeliveryAttempt
Workspace 1 ─── N Agent
Agent N ─── N Skill vía AgentSkill
Agent 1 ─── N ToolPermission
Workspace 1 ─── N Integration
Integration 1 ─── N CredentialRef
Integration 1 ─── N MCPServer
MCPServer 1 ─── N MCPTool
Workspace 1 ─── N Operation
Operation 1 ─── N ExecutionLog
Workspace 1 ─── N Job
Workspace 1 ─── N FileAsset
FileAsset 1 ─── 0..1 AudioAsset
FileAsset 1 ─── 0..1 Document
```

---

# 29. Reglas de integridad

## 29.1. Workspace

- Todo recurso debe pertenecer a un workspace.
- No permitir relaciones entre workspaces sin un mecanismo explícito.
- Las consultas deben aplicar workspace antes de búsqueda semántica.

## 29.2. Memoria

- No crear arista hacia nodo inexistente.
- No usar contenido eliminado en resultados.
- Invalidar embeddings al borrar.
- Mantener procedencia.

## 29.3. Recordatorios

- `occurrence_key` único.
- Una ocurrencia entregada no vuelve a `pending` salvo operación de reparación explícita.
- Completar una ocurrencia no debe completar automáticamente la regla recurrente.

## 29.4. Agentes

- Una skill activa debe existir.
- Una tool call requiere permiso vigente.
- Un agente archivado no puede crear operaciones nuevas.

## 29.5. Archivos

- Un archivo no debe pertenecer a varios workspaces sin copia o referencia controlada.
- El borrado debe propagarse a assets derivados.

---

# 30. Estados y transiciones

## 30.1. MemoryNode

```text
active → superseded
active → expired
active → deleted
superseded → deleted
expired → deleted
```

## 30.2. Reminder

```text
active → paused
active → completed
active → cancelled
paused → active
paused → cancelled
```

## 30.3. ReminderOccurrence

```text
pending → queued
queued → sending
sending → delivered
sending → failed
failed → retrying
retrying → sending
pending → cancelled
pending → snoozed
snoozed → pending
```

## 30.4. Integration

```text
disconnected → connecting
connecting → healthy
connecting → degraded
healthy → reauth_required
healthy → revoked
degraded → healthy
```

---

# 31. Índices recomendados

```text
users(email)
workspace_members(user_id, workspace_id)
memory_nodes(workspace_id, type, status)
memory_nodes(workspace_id, created_at)
memory_nodes(workspace_id, sensitivity)
memory_edges(workspace_id, source_node_id)
memory_edges(workspace_id, target_node_id)
reminders(workspace_id, status, next_due_at)
reminder_occurrences(status, due_at)
notifications(status, created_at)
jobs(status, priority, available_at)
operations(workspace_id, status, created_at)
execution_logs(workspace_id, created_at)
file_assets(workspace_id, status)
```

Los índices vectoriales deben incluir filtros por workspace y status.

---

# 32. Cifrado y campos sensibles

## Campos potencialmente cifrados

- `Message.content_ciphertext`.
- `MemoryNode.content_ciphertext`.
- `MemoryNode.structured_data_ciphertext`.
- `MemoryEdge.properties_ciphertext`.
- `Reminder.description_ciphertext`.
- `Agent.system_prompt_ciphertext`.
- `FileAsset.original_name_ciphertext`.
- `CredentialRef.encrypted_secret`.
- `ExecutionLog.result_summary_ciphertext`.

## Campos que no deben cifrarse si se necesitan para operar

Solo después de evaluar exposición:

- `workspace_id`.
- `status`.
- `due_at` cuando el scheduler del servidor necesite procesarlo.
- `type` si se utiliza para filtros.
- `priority`.

Si se requiere confidencialidad absoluta de fechas, el scheduler deberá operar localmente o mediante un índice protegido específico. No se debe cifrar un campo operativo y luego fingir que el servidor puede programarlo.

---

# 33. Exportación JSON canónica

```json
{
  "schema_version": "1.0",
  "export_id": "export_123",
  "created_at": "2026-07-16T12:00:00Z",
  "workspace": {
    "id": "ws_123",
    "name": "Personal"
  },
  "nodes": [
    {
      "id": "mem_123",
      "type": "preference",
      "label": "Horario de reuniones",
      "content": "<encrypted>",
      "provenance": "user_confirmed",
      "authority": "explicit",
      "confidence": 1.0
    }
  ],
  "edges": [],
  "reminders": [],
  "agents": [],
  "checksums": {}
}
```

El exportador debe poder producir una variante descifrada solo cuando el usuario la solicite explícitamente y confirme el riesgo.

---

# 34. Migraciones

## 34.1. Reglas

- Cada cambio estructural tiene migración.
- Las migraciones se prueban en SQLite y PostgreSQL cuando ambas soporten la entidad.
- Las migraciones destructivas requieren backup.
- No eliminar columnas sin periodo de compatibilidad.
- Mantener `schema_version`.

## 34.2. Datos derivados

Los embeddings, índices y caches no requieren migraciones manuales; deben poder reconstruirse desde la fuente de verdad.

## 34.3. Compatibilidad de exportaciones

El importador debe indicar:

- Versión soportada.
- Campos ignorados.
- Campos transformados.
- Conflictos.
- Elementos no importados.

---

# 35. Sincronización y conflictos

## 35.1. Principio

La sincronización no debe sobrescribir silenciosamente una edición reciente.

## 35.2. Conflicto de memoria

Si dos dispositivos editan el mismo nodo:

```text
Comparar versiones
  ↓
¿Una versión es descendiente?
  ├─ Sí → aplicar la más nueva
  └─ No → marcar conflicto
```

## 35.3. Políticas

- `server_wins`.
- `client_wins`.
- `manual_merge`.
- `append_version`.

Para contenido sensible se recomienda `manual_merge`.

---

# 36. Retención y purga

## 36.1. Retención configurable

- Conversaciones.
- Audios.
- Archivos temporales.
- Logs.
- Propuestas no confirmadas.
- Backups.

## 36.2. Purga

Un job de purga debe eliminar:

- Registro principal.
- Versiones.
- Embeddings.
- Cache.
- Archivos.
- Índices.
- Referencias derivadas.

El sistema debe distinguir entre borrado lógico inmediato y eliminación física posterior.

---

# 37. Consultas frecuentes

## Próximos recordatorios

Filtrar por workspace, status activo y `next_due_at`.

## Memorias relacionadas

Combinar:

- Texto.
- Embedding.
- Entidades.
- Aristas.
- Fecha.
- Confianza.
- Sensibilidad.

## Grafo limitado

1. Encontrar nodo raíz.
2. Aplicar filtros.
3. Recorrer hasta profundidad.
4. Ordenar por relevancia.
5. Truncar.
6. Devolver `truncated`.

## Auditoría

No devolver payload completo salvo que el usuario tenga permiso y la política permita revelar el contenido.

---

# 38. Criterios de aceptación del modelo

El modelo se considera preparado cuando:

1. Se puede representar una memoria explícita.
2. Se puede representar una memoria inferida.
3. Se puede conservar procedencia.
4. Se puede editar y versionar.
5. Se puede relacionar nodos.
6. Se puede invalidar una relación.
7. Se puede crear recurrencia sin duplicar ocurrencias.
8. Se puede registrar delivery.
9. Se puede asignar una skill a un agente.
10. Se puede revocar una tool permission.
11. Se puede auditar una operación.
12. Se puede almacenar un audio temporal.
13. Se puede exportar e importar.
14. Se puede utilizar SQLite y PostgreSQL.
15. Se puede purgar un dato y sus derivados.
16. Se puede sincronizar con detección de conflictos futura.

---

# 41. Campos de versionado y sincronización

Todas las entidades mutables deben incluir los siguientes campos para soportar sincronización futura (ver [Estrategia de Sync](./11-ESTRATEGIA-SYNC-VNBOT.md)):

### 41.1. Campos obligatorios en entidades mutables

```sql
-- Campos que toda entidad mutable debe incluir
version        INTEGER NOT NULL DEFAULT 1,
device_id      TEXT,                          -- ID del dispositivo que creó/modificó
created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
deleted_at     TIMESTAMPTZ,                   -- soft delete para sync
version_vector JSONB NOT NULL DEFAULT '{}',   -- vector de versiones por dispositivo
is_conflict    BOOLEAN NOT NULL DEFAULT FALSE, -- marcado para resolución manual
```

### 41.2. Entidad `sync_operation` (fase 0.3+)

```sql
CREATE TABLE sync_operations (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id  UUID NOT NULL REFERENCES workspaces(id),
    entity_type   TEXT NOT NULL,              -- 'memory', 'reminder', 'list', etc.
    entity_id     UUID NOT NULL,
    operation     TEXT NOT NULL,              -- 'create', 'update', 'delete'
    payload       JSONB,                      -- datos de la operación
    device_id     TEXT NOT NULL,
    version       INTEGER NOT NULL,
    status        TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'synced', 'conflict', 'failed'
    attempts      INTEGER NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    synced_at     TIMESTAMPTZ
);
```

### 41.3. Entidad `sync_conflict` (fase 0.3+)

```sql
CREATE TABLE sync_conflicts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id),
    entity_type     TEXT NOT NULL,
    entity_id       UUID NOT NULL,
    local_version   JSONB NOT NULL,           -- versión del dispositivo local
    remote_version  JSONB NOT NULL,           -- versión del servidor/otro dispositivo
    local_device_id TEXT NOT NULL,
    remote_device_id TEXT NOT NULL,
    resolution      TEXT,                     -- 'local', 'remote', 'merged', 'both', NULL
    resolved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 41.4. Índices para sync

```sql
CREATE INDEX idx_sync_ops_workspace_status ON sync_operations(workspace_id, status);
CREATE INDEX idx_sync_ops_entity ON sync_operations(entity_type, entity_id);
CREATE INDEX idx_sync_conflicts_workspace ON sync_conflicts(workspace_id, resolution);
```

### 41.5. Nota de implementación

Estas tablas y campos se crean en la migración de la fase 0.3, no en el MVP inicial. Sin embargo, los campos `version`, `updated_at` y `deleted_at` sí deben existir desde el inicio porque son útiles para auditoría y exportación incluso sin sync.

---

# 42. Datos de benchmark

Para validar el rendimiento del modelo de datos, se definen los siguientes volúmenes de prueba:

| Entidad | Volumen de prueba | Notas |
|---|---|---|
| memory_nodes | 5,000 | Con texto variable (50-500 chars) |
| memory_edges | 10,000 | Incluye relaciones de confianza y procedencia |
| reminders | 1,000 | 700 activos, 200 completados, 100 expirados |
| reminders_recurring | 100 | Con reglas de recurrencia variadas |
| audit_logs | 50,000 | Para probar paginación y retención |
| sync_operations | 10,000 | Para probar procesamiento de queue |

Estos volúmenes se usan en los benchmarks automatizados definidos en el [TRD](./02-TRD-VNBOT.md) y en [Testing y Observabilidad](./12-TESTING-Y-OBSERVABILIDAD-VNBOT.md).

---

# 43. Decisiones abiertas

1. UUIDv7 o ULID como identificador definitivo.
2. Cifrado a nivel de aplicación o soporte adicional de base de datos.
3. Estrategia final de campos cifrados que necesita el scheduler.
4. Uso de JSONB o tablas específicas para propiedades de aristas.
5. Retención exacta de versiones.
6. Sistema CRDT para sincronización futura.
7. Vector store adicional para instalaciones grandes.
8. Política de alias y resolución de entidades.
9. Modelo de espacios compartidos.
10. Soporte para datos temporales bitemporales completo.

---

# 44. Conclusión

El modelo de datos de VNBOT separa claramente:

- Identidad.
- Workspaces.
- Conversaciones.
- Memorias.
- Relaciones.
- Recordatorios.
- Ocurrencias.
- Notificaciones.
- Agentes.
- Skills.
- Integraciones.
- Jobs.
- Archivos.
- Auditoría.
- Datos derivados.

La separación permite que una memoria sea visible, corregible y exportable; que un recordatorio sea persistente e idempotente; que un agente tenga permisos limitados; y que los índices o embeddings puedan reconstruirse sin perder la fuente original.

La regla central es:

> **La fuente de verdad debe ser portable y comprensible; los índices, embeddings, caches y respuestas de IA deben ser derivados y reemplazables.**
