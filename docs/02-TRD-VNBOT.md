# VNBOT — Technical Requirements Document (TRD)

> **Documento:** Technical Requirements Document
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Definición técnica
> **Fecha:** 2026-07-16
> **Licencia prevista del código:** MIT
> **Documento relacionado:** [PRD](./01-PRD-VNBOT.md)

---

# 1. Propósito y alcance

Este documento define los requisitos técnicos, restricciones, decisiones de arquitectura y criterios operativos para construir VNBOT como una plataforma multiplataforma de memoria personal, recordatorios y mini-agentes.

El TRD traduce los objetivos de producto del PRD a una arquitectura ejecutable. Especifica:

- Capas del sistema.
- Aplicaciones cliente.
- Servicios backend.
- Persistencia.
- Procesamiento asíncrono.
- Multi-LLM.
- MCP.
- Audio.
- Memoria de grafo.
- Caching.
- Seguridad técnica.
- Observabilidad.
- Docker.
- GitHub Pages.
- GitHub Releases.
- APK y desktop.
- Estrategia de escalabilidad.

El TRD no sustituye el esquema detallado de endpoints, tablas y eventos del [Esquema Backend](./03-ESQUEMA-BACKEND-VNBOT.md), ni el detalle visual del [Diseño UI/UX](./05-DISENO-UI-UX-VNBOT.md).

---

# 2. Principios técnicos

## 2.1. Separación de responsabilidades

La interfaz no debe contener las reglas críticas de negocio. El frontend puede presentar y solicitar operaciones, pero la validación final de fechas, permisos, herramientas, cuotas y persistencia debe estar en una capa de dominio compartida o en el backend.

```text
Cliente
  ↓ solicita
API
  ↓ valida autenticación y schema
Dominio
  ↓ aplica reglas
Persistencia / Cola
  ↓ ejecuta
Worker / Integración
```

## 2.2. El LLM no es una fuente de verdad

El modelo puede:

- Clasificar intención.
- Extraer campos.
- Proponer una herramienta.
- Resumir.
- Recuperar contexto.

El modelo no debe decidir sin validación:

- Una fecha final ambigua.
- El permiso de leer información.
- La autorización de un tercero.
- El envío de mensajes.
- La eliminación de datos.
- La ejecución de código arbitrario.

## 2.3. Local-first, no local-only obligatorio

VNBOT debe poder ejecutarse localmente, pero también debe soportar un servidor privado y, opcionalmente, proveedores externos. La arquitectura debe permitir que el usuario elija el nivel de privacidad que necesita.

## 2.4. Degradación controlada

Si falla un proveedor o servicio, VNBOT debe degradarse con claridad:

- Sin LLM: heurística local.
- Sin internet: cola local.
- Sin vector store: búsqueda textual.
- Sin MCP externo: memoria interna continúa operativa.
- Sin worker: la API informa que el job está pendiente, no simula éxito.

## 2.5. Operaciones idempotentes

Cualquier operación que cree, envíe, modifique o elimine datos debe poder reintentarse sin duplicar efectos.

## 2.6. Todo dato sensible tiene alcance

Las memorias, archivos, agentes y herramientas pertenecen a un usuario y/o workspace. No existen consultas globales implícitas.

## 2.7. Observabilidad como requisito no funcional

La observabilidad no es un "nice-to-have" post-launch. VNBOT debe poder diagnosticar por qué un recordatorio no se disparó, por qué una búsqueda fue lenta o por qué un MCP falló, sin acceso al contenido del usuario.

Los traces, métricas y logs se implementan con OpenTelemetry desde la primera versión.

---

# 3. Arquitectura de alto nivel

```text
┌──────────────────────────────────────────────────────────┐
│                     CLIENTES VNBOT                       │
│                                                          │
│  Web/PWA       Android APK       Desktop       CLI       │
│  React         Capacitor         Tauri        Python/Rust│
└─────────────┬───────────────┬─────────────┬─────────────┘
              │ HTTPS/WebSocket/Local IPC
              ▼
┌──────────────────────────────────────────────────────────┐
│                         API VNBOT                         │
│ Auth · Chat · Memory · Graph · Reminders · Agents · API  │
└──────────────┬───────────────┬──────────────┬─────────────┘
               │               │              │
               ▼               ▼              ▼
        Domain services     Queue         MCP Gateway
        Validation          Redis         Policy engine
        Authorization       Jobs          External tools
               │               │              │
               ▼               ▼              ▼
      SQLite/PostgreSQL   Workers       Calendar/Email/etc.
      pgvector/index      Scheduler     Graphify/MCP servers
               │
               ▼
          Object Storage
       Audio · Files · Backups
```

---

# 4. Arquitectura por perfiles de instalación

## 4.1. Perfil Demo — GitHub Pages

### Propósito

Mostrar la experiencia de VNBOT sin necesidad de backend ni credenciales reales.

### Componentes

- React/Vite compilado como sitio estático.
- Datos ficticios.
- Chat mock.
- Grafo de ejemplo.
- Mascotas y estados visuales.
- Documentación y guías.

### Restricciones

GitHub Pages no ejecuta:

- API privada.
- Worker.
- Scheduler persistente.
- LLM local.
- Base de datos servidor.
- Secretos.

La demo no debe pedir API keys reales ni almacenar información privada. Todas las respuestas de la demo deben provenir de fixtures o de un modo sandbox explícito.

## 4.2. Perfil Local — una persona

```text
vnbot-client
vnbot-local-api
SQLite
worker embebido o proceso local
LLM local opcional
filesystem cifrado
```

Adecuado para desktop, terminal y usuarios que no desean un servidor.

## 4.3. Perfil Personal Server

```text
vnbot-api
vnbot-worker
vnbot-scheduler
PostgreSQL
Redis
MinIO/S3
```

Adecuado para sincronizar varios dispositivos de una persona o una familia pequeña.

## 4.4. Perfil Full

```text
vnbot-api x N
vnbot-worker x N
vnbot-scheduler x 1 o con locks
vnbot-mcp-gateway
postgres
redis
minio
ollama opcional
observabilidad
```

Adecuado para equipos, comunidades o servidores con varios workspaces.

---

# 5. Stack tecnológico propuesto

## 5.1. Frontend web/PWA

### Recomendación

- React.
- TypeScript en modo estricto.
- Vite.
- TanStack Query para datos remotos.
- Zustand solo para estado de interfaz y sesión local controlada.
- IndexedDB mediante Dexie para datos locales.
- CSS/Tailwind con tokens propios de VNBOT.
- Canvas/WebGL opcional para el grafo.

### Motivo

La aplicación necesita ser estática para GitHub Pages, empaquetable para Capacitor y reutilizable dentro de Tauri. Un frontend desacoplado reduce la dependencia de un servidor Next.js ejecutándose permanentemente.

## 5.2. Backend

### Recomendación

- Python 3.12+.
- FastAPI.
- Pydantic v2.
- SQLAlchemy 2.
- Alembic.
- Uvicorn/Gunicorn según el despliegue.

### Motivo

Python facilita:

- Procesamiento de audio.
- Integración con Whisper.
- Modelos locales.
- Workers de IA.
- Librerías de extracción.
- Prototipado de memoria y grafos.

Si el equipo decide operar completamente en TypeScript, la alternativa es NestJS o Fastify con Drizzle. No se recomienda mantener dos backends principales en lenguajes distintos para las mismas reglas.

## 5.3. Base de datos

### SQLite

Para:

- Modo local.
- Desktop.
- Instalaciones personales sencillas.
- Tests.
- Desarrollo.

### PostgreSQL

Para:

- Servidor.
- Multiusuario.
- Workers concurrentes.
- `pgvector`.
- Row-level security.
- Escalado horizontal.

### Regla

Ambas implementaciones deben cumplir una interfaz de almacenamiento común. No se debe escribir lógica de negocio específica para PostgreSQL en el núcleo del dominio.

## 5.4. Cola y jobs

- Redis para cola, locks y rate limiting distribuido.
- Dramatiq o Celery para workers.
- Scheduler separado.
- Dead-letter queue.
- Backoff exponencial.

Para una instalación local mínima, puede existir un modo sin Redis basado en una tabla SQLite de jobs, pero este modo no debe presentarse como equivalente a una arquitectura distribuida.

## 5.5. Almacenamiento de objetos

- MinIO en self-hosting.
- S3 compatible en instalaciones administradas.
- Filesystem local para modo single-user.

Se utiliza para:

- Audios.
- Imágenes.
- Documentos.
- Backups cifrados.
- Assets descargables si el proyecto los distribuye.

---

# 6. Clientes y plataformas

## 6.1. Web/PWA

Debe proporcionar:

- Chat.
- Panel Hoy.
- Memoria.
- Grafo.
- Agentes.
- Skills.
- Configuración.
- Captura de audio mediante permiso explícito.
- Notificaciones web cuando el navegador lo permita.
- Modo offline básico.

## 6.2. Android APK

### Primera estrategia: Capacitor

Capacitor permite empaquetar la PWA y añadir:

- Notificaciones locales.
- Micrófono.
- Filesystem.
- Estado de red.
- Deep links.
- Biometría en una fase posterior.

### Limitaciones

- Tareas en segundo plano pueden estar limitadas por Android.
- La entrega de notificaciones depende de permisos y optimización de batería.
- La transcripción local puede consumir mucho almacenamiento y RAM.
- Se debe validar la compatibilidad con dispositivos de gama baja.

### Requisito

El backend seguirá siendo la fuente de verdad para recordatorios sincronizados. El APK puede mantener recordatorios locales, pero no debe depender exclusivamente de un proceso que Android pueda suspender.

## 6.3. Desktop

### Primera estrategia: Tauri

Tauri ofrece:

- Menor consumo que Electron.
- Integración con filesystem local.
- Notificaciones nativas.
- Posibilidad de usar SQLite local.
- Empaquetado para Windows, macOS y Linux.

### Electron como alternativa

Electron puede considerarse si:

- Se requieren módulos Node difíciles de integrar en Tauri.
- Se necesita un ecosistema de plugins desktop más amplio.
- El coste de memoria no es una prioridad.

No se deben mantener Tauri y Electron como productos paralelos en la primera versión.

## 6.4. CLI

La CLI debe servir para:

```bash
vnbot init
vnbot doctor
vnbot health
vnbot add "revisar presupuesto mañana"
vnbot search "wifi"
vnbot reminders list
vnbot backup create
vnbot backup restore ./backup.vnbot.zip
vnbot migrate
vnbot mcp list
```

La CLI no debe pedir que el usuario pegue secretos en argumentos visibles del historial del shell. Debe aceptar variables de entorno seguras, prompt interactivo o archivos de configuración con permisos restrictivos.

### 6.5. Reducción de superficie temprana

El TRD original diseña cuatro clientes desde el inicio (Web/PWA, APK, Desktop, CLI). Para acelerar el MVP:

- **0.1:** Solo Web/PWA. Es el cliente con mayor alcance y menor fricción.
- **0.2:** Se añade soporte Docker para autoalojamiento (es deployment, no un cliente nuevo).
- **0.3:** Se evalúa APK (Capacitor) y Desktop (Tauri) **después** de tener la sync strategy probada y documentada (ver [Estrategia de Sync](./11-ESTRATEGIA-SYNC-VNBOT.md)).
- **CLI:** Se implementa como wrapper sobre la API HTTP desde 0.1, no como cliente nativo separado. Un script `vnbot` que hace `curl` a localhost es suficiente para empezar.

No se diseñan adapters de plataforma ni abstracciones prematuras hasta que exista al menos un cliente funcional.

---

# 7. Capas de software

## 7.1. Capa de presentación

Responsabilidades:

- Renderizar vistas.
- Recibir interacción.
- Mostrar estado de operaciones.
- Gestionar cache de UI.
- Mostrar errores comprensibles.
- No ejecutar reglas críticas de autorización.

## 7.2. Capa de aplicación

Responsabilidades:

- Coordinar casos de uso.
- Crear operaciones.
- Enviar jobs.
- Resolver confirmaciones.
- Coordinar transacciones.
- Exponer comandos y queries.

## 7.3. Capa de dominio

Responsabilidades:

- Reglas de recordatorios.
- Estados de memoria.
- Reglas de recurrencia.
- Entidades y relaciones.
- Políticas de riesgo.
- Idempotencia.
- Validaciones de negocio.

## 7.4. Capa de infraestructura

Responsabilidades:

- SQL.
- Redis.
- LLM providers.
- MCP transports.
- Filesystem.
- S3/MinIO.
- Notificaciones.
- Audio.

---

# 8. Módulos técnicos

## 8.1. Auth y sesión

- Registro local opcional.
- Login.
- Sesiones revocables.
- Cookies HttpOnly para servidores web.
- Argon2id.
- MFA posterior.
- Diferenciación entre sesión de cuenta y desbloqueo de bóveda.

## 8.2. Chat Orchestrator

Recibe una entrada y coordina:

1. Normalización.
2. Clasificación.
3. Recuperación de contexto.
4. Selección de skill.
5. Extracción estructurada.
6. Validación.
7. Confirmación.
8. Ejecución.
9. Auditoría.

## 8.3. Memory Engine

- Nodos.
- Aristas.
- Procedencia.
- Confianza.
- Sensibilidad.
- Expiración.
- Búsqueda textual.
- Búsqueda vectorial.
- Búsqueda por relaciones.
- Correcciones y contradicciones.

## 8.4. Reminder Engine

- Reglas de recurrencia.
- Ocurrencias concretas.
- Zona horaria.
- Ventanas de silencio.
- Prioridad.
- Canales.
- Reintentos.
- Idempotencia.
- Delivery log.

## 8.5. LLM Router

- Adaptadores por proveedor.
- Modelos locales.
- Fallback.
- Circuit breaker.
- Presupuesto.
- Conteo de tokens.
- Selección por tarea.
- Política de datos.

## 8.6. MCP Gateway

- Registro de servidores.
- Transportes stdio y Streamable HTTP.
- Descubrimiento de tools/resources.
- Scopes.
- Policy engine.
- Timeouts.
- Auditoría.
- Healthcheck.

## 8.7. Audio Pipeline

- Captura.
- Carga.
- Normalización.
- Transcripción.
- Revisión.
- Extracción.
- Retención/borrado.

## 8.8. Notification Service

Canales iniciales:

- Notificación web.
- Notificación desktop.
- Notificación Android.
- Email posteriormente.
- Telegram posteriormente.

Cada canal debe tener estado de entrega y reintentos independientes.

---

# 9. Flujo técnico de una instrucción

```text
1. Cliente envía mensaje
2. API valida sesión y tamaño
3. Se crea operation_id
4. Se guarda mensaje de entrada con política de retención
5. Router clasifica intención
6. Se recupera contexto mínimo autorizado
7. LLM o heurística produce JSON
8. Pydantic valida el JSON
9. Policy engine calcula riesgo
10. Si falta dato → NEEDS_CLARIFICATION
11. Si requiere aprobación → WAITING_CONFIRMATION
12. Si está autorizado → crea comando
13. Dominio ejecuta o encola job
14. Worker realiza integración si corresponde
15. Resultado se audita
16. Cliente recibe estado final
```

## 9.1. Estados de operación

```text
RECEIVED
CLASSIFYING
NEEDS_CLARIFICATION
PROPOSED
WAITING_CONFIRMATION
QUEUED
EXECUTING
SUCCEEDED
RETRYING
FAILED
CANCELLED
```

Una operación no debe pasar directamente de una respuesta textual del LLM a un efecto externo irreversible.

---

# 10. Memoria y grafo

## 10.1. Implementación MVP

- Tablas `memory_nodes` y `memory_edges`.
- PostgreSQL + pgvector en servidor.
- SQLite + índice local en instalación personal.
- Profundidad máxima visible configurable.
- Top-K por relevancia.
- Procedencia obligatoria.
- Confianza separada de importancia.

## 10.2. Tipos de nodos

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
```

## 10.3. Tipos de relaciones

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
```

## 10.4. Graphify

Graphify será un adaptador opcional para información estructural de repositorios y otros datos compatibles. No reemplaza el Memory Engine personal.

VNBOT debe poder:

- Conectarse mediante MCP.
- Mostrar estado y scopes.
- Consultar datos autorizados.
- Crear referencias cruzadas.
- Mantener separadas las memorias personales y las de código.

## 10.5. Benchmarks de rendimiento del grafo

VNBOT debe definir objetivos de rendimiento para la memoria de grafo antes de la fase de implementación (0.4/0.5). Sin benchmarks, no se puede medir regresiones ni decidir cuándo una optimización es necesaria.

### 10.5.1. Escenario de referencia

| Parámetro | Valor objetivo |
|---|---|
| Nodos totales | 5,000 |
| Edges totales | 10,000 |
| Profundidad máxima de consulta | 3 |
| Top-K por consulta | 20 |

### 10.5.2. Latencia objetivo (P95)

| Operación | Local (SQLite) | Servidor (PostgreSQL) |
|---|---|---|
| Crear nodo | < 50ms | < 30ms |
| Crear edge | < 50ms | < 30ms |
| Búsqueda textual (full-text) | < 100ms | < 80ms |
| Búsqueda semántica (vector) | < 200ms | < 100ms |
| Subgrafo (profundidad 2, 20 nodos) | < 300ms | < 150ms |
| Subgrafo (profundidad 3, 50 nodos) | < 500ms | < 250ms |
| Recorrido con filtro de confianza | < 400ms | < 200ms |
| Invalidación por borrado | < 200ms | < 100ms |

### 10.5.3. Métricas de escala

- El sistema debe degradar graciosamente (paginación, límite de profundidad) si una consulta excede los umbrales.
- Nunca cargar el grafo completo en memoria del cliente.
- Implementar `EXPLAIN ANALYZE` o equivalente en tests de integración para detectar regresiones de queries.
- Benchmark automatizado en CI para las operaciones P0.

### 10.5.4. Criterios de aceptación

- Los benchmarks se ejecutan en CI como parte del pipeline.
- Cualquier commit que degrade P95 en más de 20% en una operación P0 debe ser revisado.
- Los resultados se publican en cada release notes.

---

# 11. Multi-LLM

## 11.1. Interfaz común

```python
class LLMProvider(Protocol):
    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None,
        response_schema: dict | None,
    ) -> LLMResponse: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...
```

## 11.2. Categorías de modelos

| Tarea | Preferencia |
|---|---|
| Intención sencilla | Modelo pequeño/local |
| Extracción JSON | Modelo con structured output |
| Resumen | Modelo económico |
| Planificación | Modelo avanzado |
| Datos sensibles | Modelo local |
| Embeddings | Modelo local especializado |
| Audio | Whisper/whisper.cpp |

## 11.3. Fallback

```text
Proveedor principal
  ↓ falla temporal
Proveedor secundario
  ↓ no disponible
Modelo local
  ↓ no disponible
Heurística
```

El fallback debe indicar al usuario si la calidad o capacidad se redujo.

## 11.4. Seguridad de claves

- No guardar claves en `localStorage`.
- Usar secret store del servidor o keychain del sistema.
- Redactar valores en logs.
- Permitir claves por usuario o workspace.
- Separar clave de embedding, chat y herramienta.
- Revocar y rotar.

## 11.5. Presupuesto

Cada usuario/workspace/agente puede tener:

- Máximo de tokens.
- Coste mensual estimado.
- Máximo de llamadas por minuto.
- Máximo de tool calls por operación.
- Proveedores permitidos.

---

# 12. MCP

## 12.1. Función

MCP será el sistema de expansión de VNBOT. Permitirá conectar herramientas y recursos de forma estandarizada sin acoplar el núcleo a cada servicio.

## 12.2. MCP interno

Herramientas controladas por VNBOT:

```text
memory_search
memory_create
memory_update
memory_forget
memory_link
graph_expand
reminder_create
reminder_complete
reminder_snooze
list_manage
briefing_generate
```

## 12.3. MCP externo

Conectores posibles:

- Graphify.
- Calendarios.
- Email.
- Filesystem.
- Web/search.
- Notas.
- Mensajería oficial.

## 12.4. Seguridad

MCP no concede autorización automáticamente. El gateway deberá validar:

- Servidor confiable.
- Usuario.
- Workspace.
- Agente.
- Herramienta.
- Scope.
- Riesgo.
- Confirmación.
- Presupuesto.
- Timeout.

## 12.5. Transportes

- `stdio`: servidores locales.
- `Streamable HTTP`: servidores remotos.
- SSE solo cuando sea necesario por compatibilidad.

## 12.6. Tool result

Toda herramienta debe devolver resultado estructurado:

```json
{
  "ok": true,
  "tool": "calendar.create_event",
  "data": {},
  "source": "google-calendar",
  "operation_id": "op_123",
  "warnings": []
}
```

---

# 13. Skills y agentes

## 13.1. Skill

Una skill es una capacidad versionada que define:

- Objetivo.
- Entrada.
- Salida.
- Herramientas.
- Memoria permitida.
- Riesgo.
- Confirmación.
- Límites.

## 13.2. Agente

Un agente combina:

- Prompt.
- Modelo.
- Skills.
- Herramientas.
- Scopes de memoria.
- Nivel de autonomía.
- Presupuesto.
- Mascota.

## 13.3. Niveles de autonomía

```text
0 — Solo responder
1 — Proponer
2 — Ejecutar acciones internas
3 — Usar integraciones con confirmación
4 — Automatizar reglas explícitas y limitadas
```

## 13.4. Aislamiento

Cada agente debe tener un contexto mínimo. No debe recibir todas las memorias del usuario por defecto. El sistema debe recuperar solamente el contexto necesario para la skill activa.

---

# 14. Procesamiento asíncrono

## 14.1. Operaciones asíncronas

- Audio.
- OCR.
- Embeddings.
- Consolidación.
- Briefings.
- Sincronización MCP.
- Notificaciones.
- Backups.
- Importaciones grandes.
- Reindexación.

## 14.2. Job mínimo

```json
{
  "id": "job_123",
  "type": "send_reminder",
  "status": "pending",
  "workspace_id": "ws_123",
  "idempotency_key": "reminder_1_occurrence_20260717",
  "attempt": 0,
  "max_attempts": 5,
  "priority": "normal",
  "created_at": "..."
}
```

## 14.3. Reintentos

- Errores de red: retry.
- Error de autenticación: failed y pedir reconexión.
- Entrada inválida: failed no retryable.
- Rate limit: retry con `Retry-After`.
- Proveedor caído: circuit breaker.
- Acción externa ambigua: no retry automático.

## 14.4. Scheduler

Debe existir un scheduler dedicado o un sistema de locks. No se debe iniciar un cron completo dentro de cada réplica de API.

Para el MVP se recomienda:

```text
Scheduler único + Redis locks + workers
```

---

# 15. Cache

## 15.1. Capas

```text
UI cache       TanStack Query
Local cache    IndexedDB/SQLite
Server cache   Redis
Search index   FTS/pgvector
Asset cache    Service Worker/CDN local
```

## 15.2. Cache permitido

- Catálogo de modelos.
- Schemas MCP.
- Configuración no secreta.
- Resultados de búsqueda con TTL.
- Embeddings derivados mediante hash seguro.
- Resúmenes compactos.
- Estados de healthcheck de corta duración.

## 15.3. Cache prohibido sin protección

- Plaintext sensible.
- API keys.
- Tokens.
- Audio original.
- Respuestas completas con secretos.

## 15.4. Invalidación

Toda modificación de memoria debe invalidar:

- Búsqueda relacionada.
- Grafo del workspace.
- Embedding anterior.
- Resúmenes dependientes.
- Cache del cliente.

---

# 16. Seguridad técnica

## 16.1. Autenticación

- Argon2id.
- Sesiones rotatorias.
- Cookies seguras.
- Revocación server-side.
- MFA posterior.
- WebAuthn posterior.

## 16.2. Autorización

El backend debe comprobar `user_id`, `workspace_id`, agente, skill y herramienta en cada operación. No confiar únicamente en IDs enviados por el cliente.

## 16.3. Protección de frontend

- CSP estricta.
- Sanitización de Markdown/HTML.
- No usar `dangerouslySetInnerHTML` sin sanitizar.
- No guardar secretos en localStorage.
- Validar MIME, tamaño y extensión de archivos.
- Protección contra XSS y CSRF.

## 16.4. Protección de backend

- Rate limiting.
- Validación Pydantic.
- SSRF protection.
- Timeouts.
- Límites de payload.
- Protección contra replay.
- Logs sin contenido sensible.
- Dependencias fijadas y escaneadas.

## 16.5. Cifrado

- AES-256-GCM o XChaCha20-Poly1305.
- Argon2id para derivación de secretos derivados de contraseña.
- Salt e IV únicos.
- Envelope encryption para backups.
- Versionado del formato cifrado.
- Rotación documentada.

## 16.6. Significado de zero-knowledge

VNBOT debe documentar tres escenarios:

- El modo local estricto puede mantener plaintext fuera de terceros.
- El servidor privado puede procesar plaintext según su configuración.
- Un LLM externo puede recibir contexto. En este caso no se debe prometer zero-knowledge total.

---

# 17. Healthcheck y observabilidad

## 17.1. Endpoints

```http
GET /health/live
GET /health/ready
GET /health/dependencies
GET /metrics
```

## 17.2. `live`

Comprueba que el proceso responde. No debe marcar como fallido un proveedor opcional.

## 17.3. `ready`

Comprueba:

- Base de datos.
- Migraciones.
- Cola.
- Configuración mínima.
- Capacidad de escribir un job de prueba, si corresponde.

## 17.4. `dependencies`

Debe devolver estado resumido, latencia y versión, nunca secretos.

## 17.5. Métricas

- Latencia de API.
- Latencia de LLM.
- Tokens y coste agregado.
- Jobs pendientes.
- Jobs fallidos.
- Entregas de recordatorios.
- Errores de MCP.
- Cache hits/misses.
- Memoria y CPU del worker.
- Uso de almacenamiento.

## 17.6. Tracing

Cada operación debe tener:

- `trace_id`.
- `operation_id`.
- `job_id` si es asíncrona.
- Usuario/workspace anonimizado o interno.

Nunca se debe incluir el contenido completo de una memoria en una traza por defecto.

---

# 18. Docker y orquestación

## 18.1. Docker Compose local

El proyecto debe incluir:

- `docker-compose.local.yml`.
- `docker-compose.server.yml`.
- `.env.example`.
- Healthchecks.
- Volúmenes explícitos.
- Migración inicial.
- Backup documentado.

## 18.2. Orden de inicio

```text
PostgreSQL/SQLite
  ↓
Redis
  ↓
Migraciones
  ↓
API
  ↓
Worker
  ↓
Scheduler
  ↓
MCP Gateway
```

## 18.3. Seguridad de contenedores

- Usuario no root.
- Imagen mínima.
- Dependencias fijadas.
- Filesystem read-only cuando sea viable.
- Secrets por Docker secrets o secret manager.
- No exponer Redis públicamente.
- No exponer PostgreSQL públicamente por defecto.
- Red interna entre servicios.

## 18.4. Kubernetes posterior

No es requisito del MVP. Si se incorpora:

- Deployment separado de API y workers.
- CronJob o scheduler con locks.
- Secrets.
- Probes live/ready.
- HPA por CPU y cola.
- Persistent Volumes.
- Network Policies.
- Pod Security.

---

# 19. GitHub Pages y Releases

## 19.1. GitHub Pages

Build estático con:

- Vite.
- Fixtures.
- Service Worker opcional.
- Base path configurable.
- GitHub Actions.
- Sin secretos.
- Sin datos reales.

## 19.2. Releases

Artefactos previstos:

```text
VNBOT-Setup-x64.exe
VNBOT-linux.AppImage
VNBOT-linux.deb
VNBOT-macos.dmg
VNBOT-android.apk
checksums.txt
SBOM.spdx.json
release-notes.md
```

Cada release debe incluir:

- Versión semántica.
- Cambios.
- Migraciones.
- Compatibilidad.
- Checksums.
- Firma cuando sea posible.
- Advertencias de seguridad.
- Assets y licencias correspondientes.

---

# 20. Compatibilidad y versionado

## 20.1. API

Usar `/api/v1`. Los cambios incompatibles requieren `/api/v2` o una migración documentada.

## 20.2. Formato de exportación

Debe tener `schema_version`, manifest, checksums y metadata de cifrado. El sistema debe conservar importadores para al menos una versión anterior.

## 20.3. Skills

Cada skill tiene versión semántica. Un agente debe declarar la versión usada para facilitar reproducibilidad.

## 20.4. MCP

Guardar:

- Versión del protocolo negociada.
- Nombre y versión del servidor.
- Capabilities.
- Fecha del último handshake.
- Scopes aprobados.

---

# 21. Pruebas técnicas

## 21.1. Unitarias

- Resolución de fechas.
- Recurrencias.
- Idempotencia.
- Políticas de riesgo.
- Validación de schemas.
- Cifrado/descifrado.
- Parser heurístico.
- Permisos.

## 21.2. Integración

- API + base de datos.
- API + Redis.
- Worker + scheduler.
- Notificaciones.
- LLM mock.
- MCP mock.
- Import/export.

## 21.3. E2E

- Onboarding.
- Crear recordatorio.
- Reiniciar worker.
- Reintentar delivery.
- Editar memoria.
- Eliminar memoria.
- Modo offline.
- APK.
- Desktop.

## 21.4. Seguridad

- SAST.
- DAST.
- Escaneo de dependencias.
- Secret scanning.
- Pruebas XSS/CSRF.
- SSRF.
- Autorización entre workspaces.
- Replay de webhooks.
- MCP malicioso simulado.

## 21.5. Carga

- 10.000 memorias por workspace.
- 1.000 recordatorios activos.
- 100 ocurrencias simultáneas.
- 100 jobs concurrentes en servidor de prueba.
- 100 nodos visibles sin degradar interacción.

---

# 22. Estructura de repositorio propuesta

```text
vnbot/
├── apps/
│   ├── web/
│   ├── desktop/
│   ├── android/
│   └── cli/
├── services/
│   ├── api/
│   ├── worker/
│   ├── scheduler/
│   └── mcp-gateway/
├── packages/
│   ├── domain/
│   ├── schemas/
│   ├── ui/
│   ├── graph-ui/
│   ├── auth/
│   └── connectors/
├── skills/
├── docs/
├── infra/
│   ├── docker/
│   ├── migrations/
│   └── monitoring/
├── assets/
│   ├── mascot/
│   ├── sprites/
│   └── licenses/
├── tests/
├── .github/
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
└── README.md
```

---

# 23. Requisitos de documentación técnica

Cada módulo debe tener:

- README.
- Dependencias.
- Variables de entorno.
- Comandos de desarrollo.
- Healthcheck.
- Pruebas.
- Limitaciones.
- Política de datos.
- Licencia de dependencias relevantes.

Cada integración debe documentar:

- API oficial utilizada.
- Scopes solicitados.
- Datos que lee.
- Datos que escribe.
- Límites de frecuencia.
- Método de revocación.
- Fallback.
- Riesgos y ToS.

---

# 24. Decisiones técnicas definitivas para la siguiente fase

1. Frontend desacoplado con React/Vite.
2. FastAPI como backend de referencia.
3. SQLAlchemy/Alembic para SQLite y PostgreSQL.
4. IndexedDB para PWA; SQLite para local/desktop.
5. Redis + worker en servidor.
6. Scheduler separado con idempotencia.
7. Tauri para desktop.
8. Capacitor para el primer APK.
9. GitHub Pages únicamente para demo/documentación.
10. MCP mediante gateway con policy engine.
11. Graphify como integración opcional.
12. Heurística como fallback obligatorio.
13. No almacenar API keys en localStorage.
14. No usar `node-cron` como scheduler distribuido.
15. No usar `Map` in-memory como rate limit de producción.
16. No afirmar zero-knowledge donde exista procesamiento cloud.

---

# 25. Criterios de aprobación del TRD

El TRD se considera aprobado cuando el equipo pueda responder afirmativamente:

- ¿Se puede ejecutar VNBOT localmente sin servicios cloud?
- ¿Se puede desplegar en Docker con una ruta clara de backup?
- ¿El mismo dominio funciona en web, APK y desktop?
- ¿Los recordatorios sobreviven reinicios y reintentos?
- ¿La arquitectura separa API, workers y scheduler?
- ¿Los agentes tienen permisos explícitos?
- ¿MCP está aislado del dominio crítico?
- ¿Se puede sustituir el proveedor LLM?
- ¿El usuario puede exportar y eliminar sus datos?
- ¿El sistema tiene healthchecks y logs útiles sin filtrar contenido privado?
- ¿La demo de GitHub Pages funciona sin backend?
- ¿Los assets y dependencias tienen una estrategia de licencia clara?

---

# 26. Conclusión

VNBOT requiere una arquitectura modular porque combina memoria, recordatorios, IA, audio, agentes, MCP y distribución multiplataforma. El riesgo principal no es que la tecnología sea insuficiente; es construir demasiadas capacidades dentro de un único proceso y una única interfaz sin separar responsabilidades.

La arquitectura propuesta prioriza:

- Un núcleo de dominio pequeño.
- Persistencia intercambiable.
- Workers durables.
- Scheduler confiable.
- Proveedores LLM reemplazables.
- MCP controlado por políticas.
- Clientes multiplataforma con contratos comunes.
- Distribución reproducible.
- Observabilidad sin invadir la privacidad.

La regla técnica central de VNBOT es:

> El modelo interpreta, el dominio valida, el worker ejecuta y la auditoría explica lo ocurrido.

Con esta separación, VNBOT puede crecer desde una instalación local individual hasta una plataforma autoalojable con múltiples agentes e integraciones sin sacrificar control, seguridad ni mantenibilidad.

---

# 27. Estrategia de testing

VNBOT requiere una estrategia de testing definida desde el día uno. Ver documento completo en [Testing y Observabilidad](./12-TESTING-Y-OBSERVABILIDAD-VNBOT.md).

## 27.1. Tipos de tests por capa

| Capa | Tipo | Cobertura mínima | Herramienta sugerida |
|---|---|---|---|
| Dominio (memoria, recordatorios, grafo) | Unit | 80% | Vitest / pytest |
| API endpoints | Integration | 70% | Supertest / httpx |
| LLM Router | Unit + Contract | 60% | Vitest + mocks |
| MCP Gateway | Contract | 80% | Pact / custom |
| Workers / Scheduler | Integration | 60% | pytest + fixtures |
| Frontend (Web/PWA) | Unit + Component | 60% | Vitest + Testing Library |
| E2E | E2E | Flujos críticos | Playwright |
| Seguridad | SAST/DAST | N/A | Semgrep + OWASP ZAP |

## 27.2. Tests obligatorios por PR

- Todos los tests unitarios pasan.
- Tests de integración de módulos afectados pasan.
- Linter y typecheck sin errores.
- Sin violaciones de seguridad en Semgrep.
- Sin secretos en Gitleaks.

## 27.3. Tests obligatorios por release

- Suite E2E completa pasa.
- Benchmarks del grafo no degradan más de 20%.
- Accesibilidad (axe-core) sin violaciones AA críticas.
- Dependencias auditadas (npm audit / pip-audit).

---

# 28. Observabilidad

## 28.1. Estándar

VNBOT usa OpenTelemetry como estándar de observabilidad. Todos los servicios deben emitir:

- **Traces:** para seguir una operación a través de las capas (cliente → API → dominio → storage → LLM/MCP).
- **Metrics:** contadores, histograms y gauges por módulo.
- **Logs:** estructurados en JSON con correlation ID.

## 28.2. Instrumentación mínima por módulo

| Módulo | Spans obligatorios | Métricas obligatorias |
|---|---|---|
| API | Cada endpoint | Latencia P50/P95/P99, error rate, request count |
| Dominio | Cada operación de negocio | Duración, éxito/fallo |
| LLM Router | Cada llamada a LLM | Tokens in/out, latencia, coste, provider |
| MCP Gateway | Cada tool call | Latencia, éxito/fallo, tool name |
| Workers | Cada job | Duración, reintentos, fallos |
| Scheduler | Cada tick | Jobs ejecutados, jobs encolados |
| Storage | Cada query lenta (>100ms) | Query duration, connection pool |

## 28.3. Dashboards

- Por release: dashboard con métricas clave del sistema.
- Por módulo: vista detallada de spans y métricas.
- Alertas: definidas a partir de v0.2 para el modo servidor.

## 28.4. No recopilar contenido privado

Los traces y logs nunca deben incluir el contenido de memorias, mensajes de chat, ni datos personales. Solo se registran metadatos operativos (IDs, duraciones, estados, tipos).
