# VNBOT — MCP, Skills y Mini-agentes

> **Documento:** Model Context Protocol, skills y agentes personalizables
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Diseño de extensibilidad y autonomía
> **Fecha:** 2026-07-16
> **Documentos relacionados:** [PRD](./01-PRD-VNBOT.md), [TRD](./02-TRD-VNBOT.md), [Backend](./03-ESQUEMA-BACKEND-VNBOT.md), [Seguridad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md)

---

# 1. Propósito

VNBOT debe poder crecer sin que cada nueva capacidad obligue a modificar el núcleo de memoria, recordatorios y usuarios. Para ello utilizará dos mecanismos relacionados, pero diferentes:

- **MCP:** protocolo para conectar herramientas, recursos y prompts externos o internos.
- **Skills:** capacidades de comportamiento versionadas que indican cómo realizar una tarea y qué herramientas necesitan.

Los agentes son la combinación de:

```text
Modelo
+ instrucciones
+ skills
+ memoria permitida
+ herramientas permitidas
+ política de autonomía
+ presupuesto
+ identidad visual
```

La extensibilidad no debe significar autoridad ilimitada. Un agente puede saber cómo usar una herramienta, pero el policy engine decide si tiene permiso para usarla en una operación concreta.

---

# 2. Principios

## 2.1. MCP no es autorización

MCP define cómo intercambiar contexto y herramientas. No decide si una acción es segura para VNBOT. La autorización se implementa en el gateway y en el dominio.

## 2.2. Deny by default

Una herramienta nueva aparece deshabilitada hasta que:

- Se registra.
- Se inspecciona.
- Se asigna un scope.
- Se revisa su riesgo.
- El usuario la activa.

## 2.3. El LLM propone, el policy engine decide

```text
LLM → propone tool call
Schema → valida argumentos
Policy → valida permiso/riesgo
Usuario → confirma cuando aplica
Executor → ejecuta
Audit → registra
```

## 2.4. Memoria mínima

Un agente recibe el mínimo contexto necesario para una skill. No se inyecta toda la bóveda por defecto.

## 2.5. Herramientas pequeñas

Las tools deben tener responsabilidades concretas. Es preferible:

```text
calendar.create_event
calendar.list_events
calendar.delete_event
```

en lugar de:

```text
system.do_anything
```

## 2.6. Reversibilidad

Las acciones deben ser reversibles o requerir confirmación si no lo son.

## 2.7. Versionado

MCP servers, tools, skills, manifests y agentes deben poder versionarse y migrarse.

---

# 3. Conceptos

## 3.1. MCP Host

La aplicación VNBOT que coordina agentes, memoria, usuarios y servidores MCP.

## 3.2. MCP Client

Componente dentro del gateway que se conecta a un servidor MCP concreto.

## 3.3. MCP Server

Proceso o servicio que expone tools, resources o prompts.

## 3.4. Tool

Operación que puede producir efectos o consultar datos.

Ejemplos:

```text
memory.search
calendar.create_event
email.create_draft
filesystem.read
```

## 3.5. Resource

Información consultable que no debería producir efectos laterales importantes.

Ejemplos:

```text
memory://workspace/summary
calendar://today
project://vnbot/graph
```

## 3.6. Prompt

Plantilla reutilizable que ayuda a un cliente o agente a iniciar una tarea. No debe sustituir una skill versionada ni una política de seguridad.

## 3.7. Skill

Unidad funcional de comportamiento. Define objetivo, schemas, herramientas, memoria, riesgo y confirmación.

## 3.8. Agente

Configuración persistente que selecciona modelo, instrucciones, skills, memoria, herramientas, autonomía y avatar.

---

# 4. Arquitectura MCP de VNBOT

```text
┌──────────────────────────────────────────────┐
│                VNBOT CLIENTS                 │
│ Web · Android · Desktop · CLI                │
└─────────────────────┬────────────────────────┘
                      ▼
┌──────────────────────────────────────────────┐
│              VNBOT API / ORCHESTRATOR        │
│ Conversations · Operations · Agents · Policy │
└─────────────────────┬────────────────────────┘
                      ▼
┌──────────────────────────────────────────────┐
│                 MCP GATEWAY                  │
│ Registry · Scopes · Router · Timeouts · Audit│
└───────────────┬──────────────┬───────────────┘
                │              │
                ▼              ▼
        MCP internal      MCP external
        memory/tools      Graphify/calendar/email
```

## 4.1. MCP interno

Implementado por VNBOT y controlado por su dominio:

```text
memory_search
memory_create
memory_update
memory_forget
memory_link
graph_expand
reminder_create
reminder_update
reminder_complete
reminder_snooze
list_create
list_update
briefing_generate
```

## 4.2. MCP externo

Servidores registrados por el usuario o el administrador:

- Graphify.
- Calendarios.
- Email.
- Filesystem.
- Notas.
- Web/search.
- Mensajería oficial.
- Herramientas de desarrollo.

---

# 5. Registro de servidores MCP

## 5.1. Flujo de registro

```text
Usuario pulsa Añadir MCP
  ↓
Selecciona local o remoto
  ↓
Introduce comando/endpoint
  ↓
VNBOT valida formato
  ↓
Realiza handshake
  ↓
Descubre capabilities/tools/resources
  ↓
Clasifica riesgo
  ↓
Usuario selecciona scopes
  ↓
Healthcheck
  ↓
Guardar configuración
  ↓
Servidor disponible de forma controlada
```

## 5.2. Registro local

```json
{
  "name": "graphify-local",
  "transport": "stdio",
  "command": "graphify",
  "args": ["mcp", "serve"],
  "working_directory": "/home/user/projects/vnbot",
  "allowed_paths": ["/home/user/projects/vnbot"]
}
```

El comando debe ejecutarse con un usuario sin privilegios y con directorios limitados.

## 5.3. Registro remoto

```json
{
  "name": "calendar-server",
  "transport": "streamable_http",
  "endpoint": "https://mcp.example.com/mcp",
  "auth_type": "oauth2",
  "scopes": ["calendar.read"]
}
```

Las credenciales se almacenan en un secret store. No se guardan en el documento de configuración público.

## 5.4. Estado del servidor

```text
not_configured
connecting
healthy
degraded
reauth_required
blocked
revoked
offline
```

---

# 6. Handshake y descubrimiento

## 6.1. Información almacenada

- Protocol version.
- Server name.
- Server version.
- Capabilities.
- Tools descubiertas.
- Resources descubiertos.
- Prompts descubiertos.
- Último handshake.
- Último healthcheck.
- Errores recientes.

## 6.2. No confiar automáticamente

Que una tool aparezca en el descubrimiento no significa que esté habilitada. Las tools nuevas se registran como:

```text
DISCOVERED → REVIEW_REQUIRED → ENABLED/DISABLED
```

## 6.3. Cambios de capabilities

Si un servidor modifica sus tools o schemas:

1. Comparar versión anterior y nueva.
2. Detectar scopes nuevos.
3. Marcar cambios de riesgo.
4. Pausar tools afectadas si el riesgo aumenta.
5. Pedir revisión al usuario.

---

# 7. Scopes y permisos

## 7.1. Scopes iniciales

```text
graph.read
graph.write
memory.read
memory.write
memory.delete
calendar.read
calendar.write
calendar.delete
email.read
email.draft
email.send
filesystem.read
filesystem.write
web.fetch
notification.send
```

## 7.2. Niveles de permiso

```text
deny
read
write
execute
admin
```

La semántica depende de la tool. `admin` no debe ser una autorización genérica para todo el sistema.

## 7.3. ToolPermission

```text
ToolPermission
- agent_id
- integration_id
- tool_name
- permission_level
- scope_json
- requires_confirmation
- max_calls_per_operation
- max_calls_per_day
- created_by_user_id
- revoked_at
```

## 7.4. Matriz de permisos

La UI debe presentar una matriz comprensible:

```text
Agente: Beacon

Memoria personal       Leer ✓   Escribir ✓   Borrar ✕
Calendario             Leer ✓   Crear ✓      Borrar ✕
Correo                 Leer ✕   Borrador ✕   Enviar ✕
Filesystem             Leer ✕   Escribir ✕
Graphify               Leer ✓   Escribir ✕
```

---

# 8. Clasificación de riesgo

## 8.1. Riesgo bajo

- Buscar memoria.
- Leer calendario.
- Listar tareas.
- Consultar healthcheck.
- Crear una lista local.
- Generar un resumen.

## 8.2. Riesgo medio

- Crear memoria.
- Crear recordatorio.
- Crear evento.
- Actualizar una preferencia.
- Sincronizar un documento.

## 8.3. Riesgo alto

- Leer emails completos.
- Crear borradores.
- Compartir información.
- Leer directorios personales.
- Enviar notificaciones a terceros.
- Modificar eventos existentes.

## 8.4. Riesgo crítico

- Enviar emails.
- Borrar datos masivamente.
- Escribir archivos arbitrarios.
- Cambiar permisos.
- Acciones financieras.
- Ejecutar comandos del sistema.

Estas acciones no estarán disponibles en el MVP o exigirán confirmación fuerte, reautenticación y límites adicionales.

---

# 9. Confirmaciones

## 9.1. Confirmación simple

Para acciones de riesgo bajo/medio:

```text
Voy a crear este recordatorio:
Título: Revisar presupuesto
Fecha: lunes 20 de julio, 09:00
Agente: Beacon

[Confirmar] [Editar] [Cancelar]
```

## 9.2. Confirmación fuerte

Para acciones de riesgo alto:

- Mostrar tool exacta.
- Mostrar destino.
- Mostrar contenido completo.
- Mostrar scopes utilizados.
- Mostrar agente.
- Requerir interacción explícita.
- Solicitar reautenticación si es necesario.

## 9.3. Confirmación caducada

Una propuesta no confirmada después de su TTL debe pasar a `EXPIRED`. Si el usuario intenta confirmarla, debe recalcularse.

---

# 10. Herramientas internas de memoria

## `memory_search`

Entrada:

```json
{
  "query": "pendientes con Daniel",
  "limit": 10,
  "types": ["task", "reminder", "person"],
  "scope": "personal"
}
```

Reglas:

- Filtrar workspace.
- Aplicar scope de memoria.
- No devolver secretos si el agente no tiene permiso.
- Incluir fuente y confianza.

## `memory_create`

Debe recibir un payload estructurado y no permitir que el LLM decida directamente el workspace.

## `memory_update`

Debe utilizar versionado optimista y detectar conflictos.

## `memory_forget`

- Requiere motivo/confirmación según cantidad.
- No borrar silenciosamente relaciones críticas.
- Devuelve resumen de lo eliminado.

## `memory_link`

Valida que ambos nodos estén en el workspace y que la relación sea válida.

## `graph_expand`

Acepta profundidad y máximo de nodos. Nunca devuelve el grafo completo por defecto.

---

# 11. Herramientas de recordatorios

## `reminder_create`

Requiere:

- Título.
- Fecha/hora o regla.
- Zona horaria.
- Canal.
- Política de confirmación.

No debe aceptar una fecha ambigua como válida.

## `reminder_update`

Debe indicar si modifica:

- La regla futura.
- La próxima ocurrencia.
- Todas las ocurrencias.

## `reminder_complete`

Distingue entre completar una ocurrencia y completar la regla completa.

## `reminder_snooze`

Valida nueva fecha y ventana de silencio.

---

# 12. Herramientas externas

## 12.1. Calendario

### Lectura

Puede estar permitida sin confirmación si el usuario otorgó `calendar.read`.

### Escritura

Debe mostrar:

- Calendario destino.
- Título.
- Participantes.
- Fecha.
- Descripción.
- Zona horaria.

### Borrado

Requiere confirmación fuerte y debe conservar el evento externo original en el log mínimo necesario.

## 12.2. Email

Fases:

1. Lectura limitada.
2. Clasificación.
3. Borrador.
4. Revisión humana.
5. Envío posterior, no MVP.

Nunca se debe dar `email.send` a un agente solo por activar una skill de email.

## 12.3. Filesystem

- Directorios allowlisted.
- Solo lectura inicialmente.
- Sin path traversal.
- No usar rutas enviadas sin normalización.
- No escribir archivos en MVP.

## 12.4. Web

- Proxy seguro.
- Bloqueo de redes privadas.
- URLs permitidas.
- Límite de tamaño.
- Contenido externo no confiable.
- No seguir instrucciones encontradas en la página como si fueran policy.

## 12.5. Graphify

- Integración opcional.
- Inicialmente solo lectura.
- Mostrar origen externo.
- No mezclar automáticamente nodos personales.
- Permitir referencias cruzadas explícitas.

---

# 13. Skills

## 13.1. Estructura

Cada skill debe tener:

```text
id
version
name
description
license
author/source
risk_level
required_tools
memory_scopes
confirmation_policy
input_schema
output_schema
instructions
```

## 13.2. Manifest YAML

```yaml
id: reminder.create
version: 1.0.0
name: Crear recordatorio
description: Convierte lenguaje natural en un recordatorio validado
license: MIT
risk_level: low
required_tools:
  - reminder_create
memory_scopes:
  - personal
confirmation_policy: required_if_ambiguous
input_schema: schemas/reminder-input.json
output_schema: schemas/reminder-output.json
```

## 13.3. Instrucciones de skill

```markdown
# Crear recordatorio

## Objetivo
Crear una intención de recordatorio sin inventar datos.

## Reglas
- Interpretar fecha según zona horaria del workspace.
- Mostrar fecha completa.
- Pedir hora si falta.
- No contactar terceros sin consentimiento.
- No confirmar éxito antes de persistir.
```

## 13.4. Skills iniciales

```text
capture.note
capture.audio
memory.save
memory.search
memory.correct
memory.forget
memory.link
reminder.create
reminder.edit
reminder.snooze
reminder.complete
list.manage
briefing.daily
briefing.weekly
graph.explore
calendar.read
calendar.create_event
email.draft
mcp.connect
```

---

# 14. Ciclo de vida de una skill

```text
available
  ↓
review_required
  ↓
installed
  ↓
assigned_to_agent
  ↓
enabled
  ↓
updated/paused
  ↓
revoked/uninstalled
```

## 14.1. Instalación

- Validar manifest.
- Validar schemas.
- Revisar licencia.
- Revisar scopes.
- Comparar riesgo.
- Registrar versión.
- Ejecutar test de simulación.

## 14.2. Actualización

Si cambia cualquiera de estos campos:

- `required_tools`.
- `memory_scopes`.
- `risk_level`.
- `confirmation_policy`.

se requiere revisión del usuario.

## 14.3. Desinstalación

Deshabilitar skill, revocar asignaciones y conservar los datos creados salvo que el usuario solicite borrarlos.

---

# 15. Agentes

## 15.1. Configuración

```text
Agent
- name
- description
- avatar
- model
- system instructions
- skills
- memory scopes
- tools
- autonomy level
- budget
- schedule
- status
```

## 15.2. Agentes iniciales

### VNBOT Core

Asistente general de bajo riesgo. Puede buscar memoria y proponer recordatorios.

### Archivista

Orientado a guardar, organizar y recuperar memorias. No tiene herramientas externas por defecto.

### Beacon

Orientado a recordatorios y tareas. Puede crear y gestionar recordatorios internos.

### Navigator

Orientado a calendario. Inicia con lectura y propone eventos.

### Forge

Orientado a proyectos e ideas. Puede crear listas, notas y relaciones.

### Sentinel

Orientado a seguridad, permisos, healthchecks y auditoría. No ejecuta acciones externas.

### Scout

Orientado a investigación con web/MCP cuando el usuario lo autoriza. Trata el contenido externo como no confiable.

## 15.3. Mascota

Cada agente tiene:

- `avatar_id`.
- Paleta.
- Sprite base.
- Estados.
- Animación.

La mascota cambia de estado según la operación real, no según una animación decorativa independiente.

---

# 16. Niveles de autonomía

## Nivel 0 — Responder

El agente solo genera respuestas. No crea datos.

## Nivel 1 — Proponer

Puede presentar memorias, recordatorios o tool calls para aprobación.

## Nivel 2 — Acciones internas

Puede crear y modificar datos internos según skills permitidas.

## Nivel 3 — Integraciones confirmadas

Puede preparar acciones externas y ejecutarlas después de confirmación.

## Nivel 4 — Automatización limitada

Puede ejecutar reglas explícitas bajo:

- Horario.
- Presupuesto.
- Lista cerrada de herramientas.
- Máximo de llamadas.
- Registro.
- Botón de parada.

Nunca debe existir una opción “sin límites” en el sentido de acceso total al sistema.

---

# 17. Memoria accesible por agente

## 17.1. Scopes de memoria

```text
personal
work
study
family
project:vnbot
sensitive
secret
```

## 17.2. Reglas

- `secret` no se incluye en prompts externos.
- Un agente solo consulta scopes asignados.
- Los scopes se filtran antes del LLM.
- La UI muestra qué scopes utiliza.
- Un agente no puede cambiar sus propios scopes.

## 17.3. Context assembly

```text
User request
  ↓
Skill active
  ↓
Memory scopes
  ↓
Relevant retrieval
  ↓
Redaction
  ↓
Prompt context
```

---

# 18. Router de agentes

## 18.1. Selección explícita

El usuario puede elegir agente desde el chat.

## 18.2. Selección automática

Puede existir un router que proponga un agente según intención, pero:

- No puede aumentar permisos.
- Debe mostrar agente activo.
- Debe permitir cambiarlo.
- Debe registrar la decisión.

## 18.3. Regla de fallback

Si el agente no está disponible:

```text
Agente específico
  ↓ no disponible
VNBOT Core
  ↓ no disponible
Heurística o modo manual
```

---

# 19. Orquestación de operaciones

## 19.1. Flujo

```text
Usuario
  ↓
Router de intención
  ↓
Selector de skill
  ↓
Agente
  ↓
Retriever
  ↓
LLM
  ↓
Structured output
  ↓
Policy engine
  ↓
Confirmación
  ↓
Tool executor
  ↓
Auditoría
```

## 19.2. Multiagente futuro

```text
Supervisor
├── Archivista
├── Beacon
├── Navigator
├── Forge
└── Scout
```

El supervisor debe pasar contexto mínimo y no compartir automáticamente toda la memoria entre agentes.

## 19.3. Prohibición inicial

No permitir cadenas autónomas indefinidas de agentes. Cada operación tiene:

- Profundidad máxima.
- Número máximo de tool calls.
- Presupuesto.
- Timeout.
- Estado cancelable.

---

# 20. Presupuesto y límites

## 20.1. Límites por agente

```text
max_tokens_per_operation
max_cost_per_day
max_tool_calls_per_operation
max_external_calls_per_hour
max_memory_results
max_graph_depth
max_file_bytes
```

## 20.2. Presupuesto por workspace

El workspace puede limitar el gasto total, uso de proveedores o número de integraciones.

## 20.3. Exceso de presupuesto

El sistema debe detenerse con estado explícito:

```text
BUDGET_EXCEEDED
```

No debe cambiar silenciosamente a un proveedor más costoso.

---

# 21. Tool execution

## 21.1. Preflight

Antes de ejecutar:

- Tool existe.
- Servidor healthy.
- Schema válido.
- Scope presente.
- Usuario autorizado.
- Presupuesto disponible.
- Confirmación vigente.
- Idempotency key.

## 21.2. Ejecución

- Timeout.
- Cancelación.
- Captura de status.
- Sanitización de resultado.
- Límite de respuesta.

## 21.3. Post-execution

- Guardar resumen.
- Actualizar recurso interno si corresponde.
- Invalidar cache.
- Registrar auditoría.
- Actualizar UI.
- Mostrar resultado y warnings.

---

# 22. Resources y privacidad

Los resources son de solo lectura en la medida de lo posible, pero pueden contener información sensible.

Cada resource debe indicar:

```text
resource_uri
workspace_scope
sensitivity
allowed_agents
cache_ttl
source
```

No se debe exponer un resource global que devuelva toda la bóveda.

---

# 23. Prompts MCP y prompts internos

Los prompts pueden facilitar experiencias predefinidas, por ejemplo:

- “Resume mi día.”
- “Revisa mis tareas atrasadas.”
- “Explora conexiones de este proyecto.”

Pero el prompt no debe ocultar:

- Qué tools se usarán.
- Qué datos se leerán.
- Qué permisos hacen falta.

Las instrucciones críticas de seguridad viven en el policy engine, no en un prompt editable por una skill.

---

# 24. Integración Graphify

## 24.1. Objetivo

Conectar VNBOT con una memoria estructural de repositorios, documentos o proyectos técnicos sin convertir Graphify en la memoria personal principal.

## 24.2. Primer alcance

- Conexión read-only.
- Consultar nodos y relaciones.
- Buscar estructura de proyecto.
- Crear referencias externas desde memorias VNBOT.
- Mostrar origen Graphify.

## 24.3. Flujo

```text
Usuario pregunta por un proyecto
  ↓
VNBOT busca memoria personal
  ↓
Si autorizado, consulta Graphify
  ↓
Une resultados como fuentes separadas
  ↓
Responde distinguiendo origen personal/externo
```

## 24.4. No hacer inicialmente

- Subir memorias personales a Graphify.
- Dar write access sin revisión.
- Mezclar nodos sin procedencia.
- Permitir que Graphify acceda a toda la bóveda.

---

# 25. Skills de alto riesgo

## Email

Primero `email.draft`, después `email.send` con confirmación fuerte.

## Filesystem

Primero lectura de directorio allowlisted. Escritura solo con path confirmado y diff mostrado.

## Web

Lectura controlada. Nunca seguir instrucciones de la página como políticas del agente.

## Compartición

Mostrar destinatario, datos y tiempo de acceso. Permitir revocación.

## Eliminación

Confirmación adicional, resumen de impacto y posibilidad de exportar antes.

---

# 26. Marketplace futuro de skills

## 26.1. Requisitos

- Manifest.
- Licencia.
- Autor.
- Repositorio origen.
- Versionado.
- Firma opcional/obligatoria según categoría.
- Scopes.
- Riesgo.
- Dependencias.
- Historial de cambios.
- Reporte de vulnerabilidad.

## 26.2. Categorías

```text
productivity
memory
calendar
research
developer
communication
security
visual
```

## 26.3. Instalación segura

- No instalar automáticamente por recomendación del LLM.
- Revisión humana.
- Preview de permisos.
- Sandbox si incluye código.
- Rollback.

---

# 27. Pruebas de MCP y skills

## Unitarias

- Validación de manifest.
- Scopes.
- Niveles de riesgo.
- Confirmación.
- Policy engine.
- Redacción de secretos.
- Presupuesto.

## Integración

- Handshake.
- Descubrimiento.
- Tool call.
- Timeout.
- Reautenticación.
- Revocación.
- Error de schema.

## Seguridad

- Tool poisoning.
- Prompt injection.
- Scope escalation.
- Servidor MCP falso.
- Respuesta gigante.
- Path traversal.
- SSRF.
- Repetición de llamada.

## UX

- Usuario entiende scopes.
- Usuario puede cancelar.
- Usuario distingue fuente externa.
- Usuario ve agente activo.
- Usuario puede simular skill.

---

# 28. Observabilidad MCP

Registrar sin contenido sensible:

- Server ID.
- Tool name.
- Agent ID.
- Skill ID.
- Duración.
- Estado.
- Código de error.
- Bytes enviados/recibidos.
- Conteo de llamadas.
- Confirmación requerida.

No registrar por defecto:

- Tokens.
- Contenido completo de tool args.
- Documentos completos.
- Credenciales.
- Prompts privados.

---

# 29. Criterios de aceptación MCP

MCP está correctamente implementado cuando:

1. Se puede registrar un servidor local o remoto.
2. El handshake queda auditado.
3. Las tools descubiertas aparecen deshabilitadas por defecto.
4. El usuario selecciona scopes.
5. El agente solo ve herramientas autorizadas.
6. Las llamadas tienen schemas.
7. Las operaciones de riesgo requieren confirmación.
8. Existen timeouts y límites.
9. El servidor puede revocarse.
10. El fallo de un MCP no rompe VNBOT.
11. Los logs no contienen secretos.
12. Graphify funciona como integración opcional.
13. Las respuestas externas se tratan como datos no confiables.

---

# 30. Criterios de aceptación de skills

Una skill está lista cuando:

- Tiene manifest.
- Tiene licencia.
- Tiene input/output schema.
- Declara herramientas.
- Declara memoria.
- Declara riesgo.
- Tiene instrucciones claras.
- Tiene tests.
- Tiene simulación.
- Tiene manejo de error.
- Puede desactivarse.
- No puede ampliar permisos sola.

---

# 31. Criterios de aceptación de agentes

Un agente está listo cuando:

- Tiene identidad y propósito.
- Tiene mascota/estado.
- Tiene modelo configurable.
- Tiene skills definidas.
- Tiene scopes de memoria.
- Tiene tools permitidas.
- Tiene autonomía explícita.
- Tiene presupuesto.
- Tiene simulación.
- Tiene auditoría.
- Puede pausarse y revocarse.

---

# 32. Flujo de desarrollo de una nueva integración

```text
Definir caso de uso
  ↓
Elegir API/protocolo oficial
  ↓
Crear adapter
  ↓
Definir scopes
  ↓
Definir riesgo
  ↓
Definir schemas
  ↓
Crear mock
  ↓
Crear healthcheck
  ↓
Implementar tool read-only
  ↓
Añadir write con confirmación
  ↓
Documentar ToS y privacidad
  ↓
Publicar como plugin/integración
```

---

# 35. Contract testing para herramientas MCP

Cada herramienta MCP integrada en VNBOT debe tener contract tests que verifiquen su comportamiento sin depender de un servidor MCP real.

### 35.1. Qué verifican los contract tests

| Aspecto | Verificación |
|---|---|
| Input schema | El schema declarado coincide con lo que la tool realmente acepta |
| Output schema | El output real coincide con el schema declarado |
| Scopes | La tool solo accede a los recursos que sus scopes permiten |
| Aislamiento | Un fallo en la tool no propaga al resto del sistema |
| Timeout | La tool respeta el timeout configurado |
| Idempotencia | Llamar la tool dos veces con los mismos args produce el mismo resultado (cuando aplica) |

### 35.2. Implementación

```text
Para cada tool MCP registrada:
1. Crear un fixture con inputs representativos (mínimo 3 casos: happy path, edge case, error).
2. Crear un mock del servidor MCP que responde según el fixture.
3. Ejecutar el contract test contra el mock.
4. En CI, también ejecutar contra el servidor MCP real (si está disponible) como smoke test.
```

### 35.3. Métricas de tools

Cada tool debe reportar:

- `vnbot_mcp_tool_calls_total{tool_name, status}` (success, error, timeout).
- `vnbot_mcp_tool_duration_seconds{tool_name}` (histogram).
- `vnbot_mcp_tool_permissions_denied{tool_name, scope}`.

Estas métricas alimentan el dashboard de observabilidad y permiten detectar tools problemáticas antes de que afecten al usuario.

---

# 36. Revisión de seguridad de nuevas herramientas

Antes de que una herramienta MCP se habilite para un usuario, debe pasar por:

1. **Registro:** nombre, descripción, schema de input/output, scopes requeridos.
2. **Inspección:** un maintainer revisa el código o la documentación de la tool.
3. **Análisis de riesgo:** ¿qué datos puede leer? ¿qué acciones puede ejecutar? ¿puede afectar otros workspaces?
4. **Asignación de scopes:** se le otorgan los mínimos necesarios.
5. **Contract tests:** los tests pasan en CI.
6. **Habilitación por defecto desactivada:** el usuario debe activarla manualmente.
7. **Auditoría:** cada llamada queda registrada.

Este proceso está documentado en [Seguridad y Privacidad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md).

---

# 37. Decisiones abiertas

1. SDK MCP principal: Python, TypeScript o ambos.
2. Transporte remoto primario.
3. Soporte de OAuth MCP.
4. Firma obligatoria de servidores.
5. Sandbox para servidores stdio.
6. Marketplace incluido o repositorio separado.
7. Formato definitivo de skills.
8. Sistema de evaluación automática de skills.
9. Persistencia de schemas descubiertos.
10. Multiagente en VNBOT 1.0 o posterior.

---

# 38. Conclusión

MCP y las skills permiten que VNBOT crezca desde una aplicación de recordatorios hasta una plataforma de agentes personalizables. Pero esa expansión solo es sostenible si cada capacidad tiene límites claros.

La arquitectura de VNBOT queda definida así:

```text
Skill describe cómo trabajar.
Agente define quién trabaja.
MCP conecta qué puede usar.
Policy engine decide si puede usarlo.
Usuario confirma cuando el riesgo lo exige.
Auditoría registra lo ocurrido.
```

La regla central es:

> **Una herramienta puede estar conectada sin estar autorizada; un agente puede conocer una skill sin tener permiso para ejecutarla.**

Con esta separación, VNBOT puede aceptar nuevos modelos, skills, servidores MCP y agentes sin convertir cada extensión en una amenaza para la privacidad o la integridad del sistema.
