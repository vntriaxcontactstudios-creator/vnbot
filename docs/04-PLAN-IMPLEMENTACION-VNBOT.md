# VNBOT — Plan de Implementación

> **Documento:** Plan de implementación
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Planificación ejecutable
> **Fecha:** 2026-07-16
> **Documentos relacionados:** [PRD](./01-PRD-VNBOT.md), [TRD](./02-TRD-VNBOT.md), [Esquema Backend](./03-ESQUEMA-BACKEND-VNBOT.md), [UI/UX](./05-DISENO-UI-UX-VNBOT.md), [Roadmap](./10-ROADMAP-VNBOT.md)

---

# 1. Propósito

Este documento transforma la visión y la arquitectura de VNBOT en una secuencia concreta de trabajo. Define qué construir primero, qué dependencias existen, cómo comprobar cada fase, cómo organizar el repositorio, cómo gestionar releases y qué funcionalidades deben posponerse para evitar que el proyecto se vuelva inmanejable.

El plan está diseñado para un proyecto open source que pueda evolucionar desde una demo estática hasta una plataforma distribuida con:

- Web/PWA.
- APK Android.
- Desktop.
- Docker.
- CLI.
- Memoria personal basada en grafo.
- Recordatorios confiables.
- Múltiples LLM.
- Skills y agentes.
- MCP.
- Integraciones oficiales.

La estrategia es incremental: cada fase debe dejar un producto ejecutable, demostrable y verificable. No se debe esperar a tener todos los agentes, canales o integraciones para publicar una primera versión.

---

# 2. Estrategia general

## 2.1. Orden de prioridades (revisado)

```text
Confiabilidad de recordatorios
        ↓
Memoria editable y recuperable
        ↓
Testing y observabilidad (cross-cutting desde el inicio)
        ↓
Modo local y exportación
        ↓
Estrategia de sincronización (antes de multiplataforma)
        ↓
Workers, scheduler y Docker
        ↓
Audio, APK y desktop
        ↓
MCP y Graphify
        ↓
Agentes y skills
        ↓
Integraciones externas
        ↓
Autonomía avanzada
```

## 2.2. Principio de núcleo pequeño

El núcleo inicial de VNBOT tendrá únicamente:

- Cuenta/modo local.
- Chat.
- Memoria.
- Grafo limitado.
- Recordatorios.
- Notificaciones básicas.
- Exportación.
- Diagnóstico.

El resto debe implementarse como módulos, adaptadores o plugins.

## 2.3. Principio de una capacidad por vez

No se implementará simultáneamente:

- Audio remoto.
- WhatsApp.
- Gmail.
- MCP externo.
- Multiagente.
- OCR.
- Sincronización.

Cada capacidad debe probarse individualmente antes de convertirse en una dependencia de otra.

## 2.4. Definición de versión funcional

Una versión puede publicarse cuando:

- Se instala.
- Tiene documentación.
- Tiene migración si modifica datos.
- Tiene manejo de errores.
- Tiene pruebas automatizadas.
- Puede recuperarse de un fallo.
- No expone secretos.
- Tiene notas de release.

---

# 3. Fases generales

| Fase | Nombre | Resultado |
|---|---|---|
| 0 | Preparación | Repositorio, decisiones, licencia y CI |
| 1 | Demo visual | GitHub Pages con experiencia simulada |
| 2 | Núcleo local | Memoria y recordatorios sin backend remoto |
| 3 | Backend privado | API, workers, scheduler y Docker |
| 4 | Inteligencia | LLM Router, búsqueda y audio |
| 5 | Plataformas | APK, desktop y CLI |
| 6 | Grafo | Memoria visual y relaciones avanzadas |
| 7 | MCP | Gateway, permisos y Graphify |
| 8 | Agentes | Skills, mascotas y autonomía limitada |
| 9 | Integraciones | Calendario, Telegram, Gmail y otros |
| 10 | Estabilización | Seguridad, rendimiento, releases y comunidad |

---

# 4. Fase 0 — Preparación del proyecto

## Objetivo

Crear una base de repositorio que permita trabajar de forma ordenada antes de desarrollar funciones complejas.

## Entregables

- Repositorio GitHub `vnbot`.
- Licencia MIT.
- README principal.
- CONTRIBUTING.md.
- SECURITY.md.
- CODE_OF_CONDUCT.md.
- CHANGELOG.md.
- `THIRD_PARTY_NOTICES.md`.
- Estructura monorepo.
- CI inicial.
- ADRs técnicos.
- Inventario de assets.

## Tareas

### Identidad

- [ ] Definir nombre oficial: VNBOT.
- [ ] Definir logo y wordmark.
- [ ] Reservar nombres de paquetes.
- [ ] Crear guía de nomenclatura.
- [ ] Migrar referencias antiguas de MinBot-Task.

### Licencia

- [ ] Añadir MIT para código.
- [ ] Documentar licencia de documentación.
- [ ] Documentar licencia de assets.
- [ ] Auditar repositorios de terceros.
- [ ] Crear inventario de modelos y datasets visuales.

### Arquitectura

- [ ] Crear ADR sobre frontend desacoplado.
- [ ] Crear ADR sobre SQLite/PostgreSQL.
- [ ] Crear ADR sobre workers.
- [ ] Crear ADR sobre MCP.
- [ ] Crear ADR sobre cifrado y privacidad.
- [ ] Crear ADR sobre distribución.

### Calidad

- [ ] Configurar formatter.
- [ ] Configurar linter.
- [ ] Configurar type checking.
- [ ] Configurar tests.
- [ ] Configurar pre-commit.
- [ ] Configurar Gitleaks.
- [ ] Configurar Semgrep.
- [ ] Configurar Trivy para imágenes.

### Documentación y observabilidad

- [ ] Crear documento de estrategia de sincronización (11-ESTRATEGIA-SYNC-VNBOT.md).
- [ ] Crear documento de testing y observabilidad (12-TESTING-Y-OBSERVABILIDAD-VNBOT.md).
- [ ] Crear documento de gobernanza (13-GOBERNANZA-DE-PROYECTO-VNBOT.md).
- [ ] Configurar axe-core en CI para accesibilidad.
- [ ] Configurar OpenTelemetry SDK en el proyecto base.
- [ ] Definir cobertura mínima de tests por módulo.
- [ ] Crear benchmarks automatizados para el grafo.

## Criterio de salida

Un contribuidor nuevo puede clonar el repositorio, instalar dependencias, ejecutar una comprobación básica y comprender la arquitectura leyendo el README.

---

# 5. Fase 1 — Demo visual en GitHub Pages

## Objetivo

Publicar una demostración navegable del concepto sin backend, secretos ni datos reales.

## Alcance

- Landing.
- Onboarding simulado.
- Panel Hoy.
- Chat mock.
- Grafo con fixtures.
- Selector de agentes.
- Mascota principal.
- Estados visuales.
- Vista de instalación.
- Links a GitHub, Docker y Releases.

## Tareas

- [ ] Crear app Vite/React.
- [ ] Configurar base path de GitHub Pages.
- [ ] Implementar routing estático.
- [ ] Crear fixtures anónimos.
- [ ] Crear chat simulado.
- [ ] Crear tarjetas de acción.
- [ ] Crear grafo demo.
- [ ] Añadir mascot states.
- [ ] Añadir responsive.
- [ ] Añadir high contrast.
- [ ] Añadir reduced motion.
- [ ] Configurar GitHub Action de deploy.

## Reglas

- Ninguna API key.
- Ningún correo real.
- Ningún dato del usuario guardado en un servidor.
- Debe indicar qué partes son simuladas.
- Debe poder cargar sin backend.

## Criterio de salida

La persona que visita la página entiende qué es VNBOT, ve el flujo principal y puede navegar por una experiencia consistente sin instalar nada.

---

# 6. Fase 2 — Núcleo local

## Objetivo

Construir una versión utilizable para una sola persona, sin depender de un backend remoto ni de un proveedor LLM.

## Alcance funcional

- Bóveda local.
- IndexedDB en PWA.
- SQLite en desktop/local.
- Chat.
- Heurística.
- Memorias.
- Nodos y aristas básicos.
- Recordatorios locales.
- Notificaciones disponibles en plataforma.
- Exportación/importación.

## 6.1. Implementación de almacenamiento

### PWA

- [ ] Crear esquema IndexedDB.
- [ ] Añadir migraciones de cliente.
- [ ] Crear repositorios.
- [ ] Crear índices por fecha/tipo.
- [ ] Separar plaintext en memoria de UI.
- [ ] Añadir expiración de datos temporales.

### Local/desktop

- [ ] Crear SQLite adapter.
- [ ] Crear migraciones Alembic o equivalente.
- [ ] Configurar backup.
- [ ] Crear bloqueo de archivo.
- [ ] Crear comando `vnbot doctor`.

## 6.2. Memoria básica

- [ ] Crear MemoryNode.
- [ ] Crear MemoryEdge.
- [ ] Añadir procedencia.
- [ ] Añadir confianza.
- [ ] Añadir sensibilidad.
- [ ] Implementar CRUD.
- [ ] Implementar búsqueda textual.
- [ ] Implementar olvidar.
- [ ] Implementar exportación.

## 6.3. Heurística

Debe detectar al menos:

- “Recuérdame”.
- “Avísame”.
- “Tengo que”.
- “Necesito”.
- “Guarda que”.
- “Olvida que”.
- “Añade a la lista”.
- Fechas relativas comunes.
- Horas básicas.

La heurística debe indicar baja confianza cuando no pueda resolver una instrucción con seguridad.

## 6.4. Recordatorios locales

- [ ] Crear entidad Reminder.
- [ ] Crear Occurrence.
- [ ] Resolver timezones.
- [ ] Implementar recurrencia.
- [ ] Implementar posponer.
- [ ] Implementar completar.
- [ ] Implementar cancelación.
- [ ] Evitar duplicados.
- [ ] Crear historial local.

## Criterio de salida

El usuario puede crear una memoria y un recordatorio, cerrar la aplicación, abrirla de nuevo, recuperar los datos y exportarlos sin conexión.

---

# 7. Fase 3 — Backend privado

## Objetivo

Convertir el núcleo local en una plataforma servidor con API, autenticación, workers, scheduler y Docker.

## 7.1. API

- [ ] Crear FastAPI.
- [ ] Crear `/api/v1`.
- [ ] Crear schemas Pydantic.
- [ ] Crear manejo de errores.
- [ ] Crear request_id/trace_id.
- [ ] Crear OpenAPI.
- [ ] Crear autenticación.
- [ ] Crear autorización por workspace.

## 7.2. Persistencia

- [ ] Crear SQLAlchemy.
- [ ] Crear Alembic.
- [ ] Validar SQLite.
- [ ] Validar PostgreSQL.
- [ ] Crear índices.
- [ ] Crear transacciones.
- [ ] Crear soft delete.
- [ ] Crear backups.

## 7.3. Redis y jobs

- [ ] Añadir Redis.
- [ ] Definir job schema.
- [ ] Crear worker.
- [ ] Crear scheduler.
- [ ] Crear locks.
- [ ] Crear reintentos.
- [ ] Crear dead-letter queue.
- [ ] Crear endpoint de estado de jobs.

## 7.4. Docker

- [ ] Dockerfile API.
- [ ] Dockerfile worker.
- [ ] Dockerfile scheduler.
- [ ] Compose local.
- [ ] Compose server.
- [ ] `.env.example`.
- [ ] Healthchecks.
- [ ] Volúmenes.
- [ ] Usuario no root.

## 7.5. Notificaciones

- [ ] Notificación web.
- [ ] Notificación desktop.
- [ ] Notificación local Android posteriormente.
- [ ] Estado de delivery.
- [ ] Reintentos.
- [ ] Preferencias de usuario.

## Criterio de salida

Una instalación Docker puede registrar un usuario, guardar memorias, crear recordatorios, procesar jobs, reiniciarse y conservar el estado.

---

# 8. Fase 4 — Inteligencia y audio

## Objetivo

Añadir IA configurable sin convertirla en una dependencia obligatoria ni permitir que actúe sin validación.

## 8.1. LLM Router

- [ ] Definir interfaz común.
- [ ] Implementar Ollama.
- [ ] Implementar OpenAI-compatible.
- [ ] Implementar proveedor adicional.
- [ ] Añadir structured outputs.
- [ ] Añadir fallback.
- [ ] Añadir timeouts.
- [ ] Añadir circuit breaker.
- [ ] Añadir presupuesto.
- [ ] Añadir conteo de tokens agregado.

## 8.2. Clasificación

- [ ] Intent classifier.
- [ ] Extracción de fecha.
- [ ] Extracción de entidades.
- [ ] Selección de skill.
- [ ] Confidence score.
- [ ] Detección de ambigüedad.
- [ ] Validación Pydantic.

## 8.3. Búsqueda semántica

- [ ] Elegir embedding local inicial.
- [ ] Crear índice.
- [ ] Asociar vector a nodo.
- [ ] Crear búsqueda híbrida.
- [ ] Añadir filtros.
- [ ] Invalidar embeddings al editar/borrar.
- [ ] Añadir fuentes a respuesta.

## 8.4. Audio

- [ ] UI de grabación.
- [ ] Endpoint temporal.
- [ ] Validación de audio.
- [ ] Job de transcripción.
- [ ] Whisper local.
- [ ] Revisión de transcript.
- [ ] Retención configurable.
- [ ] Borrado seguro.

## 8.5. OCR posterior

- [ ] Subida de imagen.
- [ ] Job OCR.
- [ ] Preview de extracción.
- [ ] Corrección manual.
- [ ] Conversión a memoria o recordatorio.

## Criterio de salida

El sistema puede interpretar instrucciones con un modelo local o externo, mostrar una propuesta estructurada, pedir aclaraciones y ejecutar solo después de validarla.

---

# 9. Fase 5 — APK, desktop y CLI

## 9.1. APK

- [ ] Integrar PWA con Capacitor.
- [ ] Permisos de micrófono.
- [ ] Notificaciones locales.
- [ ] Estado de red.
- [ ] Filesystem local.
- [ ] Manejo de suspensión.
- [ ] Generar APK debug.
- [ ] Pruebas en dispositivos reales.
- [ ] Generar APK release.
- [ ] Firmar APK.

## 9.2. Desktop

- [ ] Crear shell Tauri.
- [ ] Integrar frontend.
- [ ] Configurar SQLite local.
- [ ] Notificaciones nativas.
- [ ] Acceso a archivos autorizado.
- [ ] Auto-lock.
- [ ] Build Windows.
- [ ] Build Linux.
- [ ] Build macOS.
- [ ] Actualización firmada posteriormente.

## 9.3. CLI

- [ ] `init`.
- [ ] `doctor`.
- [ ] `health`.
- [ ] `add`.
- [ ] `search`.
- [ ] `reminders`.
- [ ] `backup`.
- [ ] `restore`.
- [ ] `mcp`.
- [ ] Salida JSON para automatizaciones.
- [ ] No mostrar secretos en argumentos.

## Criterio de salida

El mismo usuario puede acceder a sus memorias y recordatorios desde web, APK o desktop, respetando el modelo de permisos y sincronización definido.

---

# 10. Fase 6 — Grafo de memoria

## Objetivo

Convertir la memoria básica en una representación relacional visible y útil.

## Tareas

- [ ] Definir catálogo de tipos de nodo.
- [ ] Definir catálogo de relaciones.
- [ ] Crear resolución de entidades.
- [ ] Detectar duplicados.
- [ ] Crear búsqueda por relaciones.
- [ ] Añadir profundidad configurable.
- [ ] Crear grafo limitado.
- [ ] Añadir inspector.
- [ ] Crear modo lista.
- [ ] Añadir export JSON.
- [ ] Añadir corrección de aristas.
- [ ] Añadir expiración temporal.
- [ ] Añadir contradicciones.

## Graphify

- [ ] Crear adaptador MCP.
- [ ] Registrar servidor.
- [ ] Mostrar tools/resources.
- [ ] Permitir solo `graph.read` al principio.
- [ ] Crear referencias cruzadas.
- [ ] No mezclar automáticamente datos personales.
- [ ] Crear opción de desconexión.

## Criterio de salida

El usuario puede buscar una entidad, ver sus relaciones relevantes, abrir la memoria origen, corregir una relación y eliminarla sin afectar datos no relacionados.

---

# 11. Fase 7 — MCP Gateway

## Objetivo

Crear una capa segura para conectar herramientas externas y exponer herramientas internas.

## 11.1. MCP interno

- [ ] `memory_search`.
- [ ] `memory_create`.
- [ ] `memory_update`.
- [ ] `memory_forget`.
- [ ] `graph_expand`.
- [ ] `reminder_create`.
- [ ] `reminder_complete`.
- [ ] `reminder_snooze`.
- [ ] `list_manage`.

## 11.2. Gateway

- [ ] Registro de servidor.
- [ ] Transporte stdio.
- [ ] Streamable HTTP.
- [ ] Handshake.
- [ ] Descubrimiento.
- [ ] Scopes.
- [ ] Policy engine.
- [ ] Timeouts.
- [ ] Rate limit.
- [ ] Healthcheck.
- [ ] Auditoría.
- [ ] Revocación.

## 11.3. Herramientas por riesgo

### Bajo

- Lectura de memoria autorizada.
- Consulta de estado.
- Búsqueda de nodos.

### Medio

- Crear memoria.
- Crear recordatorio.
- Crear evento.

### Alto

- Borrador de email.
- Lectura de filesystem.
- Compartir contenido.

### Crítico

- Enviar email.
- Escribir archivos.
- Eliminar datos masivamente.
- Acciones financieras, siempre fuera del MVP.

## Criterio de salida

Un servidor MCP puede conectarse, mostrar sus capacidades, recibir solo los scopes elegidos y ejecutar una herramienta con confirmación y auditoría.

---

# 12. Fase 8 — Agentes y skills

## Objetivo

Permitir personalización avanzada sin convertir las instrucciones en código arbitrario.

## Tareas

- [ ] Crear Agent entity.
- [ ] Crear Skill manifest.
- [ ] Crear selector de modelo.
- [ ] Crear selector de memoria.
- [ ] Crear selector de herramientas.
- [ ] Crear niveles de autonomía.
- [ ] Crear presupuesto por agente.
- [ ] Crear modo simulación.
- [ ] Crear auditoría por agente.
- [ ] Vincular mascota a agente.
- [ ] Implementar skills base.

## Skills iniciales

```text
memory.save
memory.search
memory.correct
memory.forget
reminder.create
reminder.snooze
reminder.complete
list.manage
briefing.daily
graph.explore
mcp.connect
```

## Criterio de salida

El usuario puede crear un agente, asignarle skills y herramientas, revisar permisos, ejecutar una prueba controlada y revocarlo.

---

# 13. Fase 9 — Integraciones oficiales

## Orden recomendado

1. Calendario interno.
2. Google Calendar.
3. Telegram Bot API.
4. Gmail lectura/borradores.
5. Outlook.
6. WhatsApp Business Cloud API.
7. Discord bot oficial.

## Reglas

Cada integración debe documentar:

- API oficial.
- Scopes.
- Datos leídos.
- Datos escritos.
- Costes.
- Límites.
- ToS.
- Revocación.
- Healthcheck.
- Fallback.

## Criterio de salida

La integración puede activarse, probarse, revocarse y operar sin que un fallo externo rompa el núcleo de VNBOT.

---

# 14. Fase 10 — Estabilización y comunidad

## Seguridad

- [ ] Threat model actualizado.
- [ ] Pentest básico.
- [ ] SAST.
- [ ] DAST.
- [ ] Secret scanning.
- [ ] Escaneo de imágenes.
- [ ] Revisión MCP.
- [ ] Revisión de archivos.
- [ ] Revisión de backups.

## Rendimiento

- [ ] Pruebas de 10.000 memorias.
- [ ] Pruebas de 1.000 recordatorios.
- [ ] Pruebas de workers.
- [ ] Pruebas de reconexión.
- [ ] Pruebas de grafo.
- [ ] Pruebas en Android de gama baja.
- [ ] Pruebas de consumo desktop.

## Releases

- [ ] Versionado semántico.
- [ ] Checksums.
- [ ] SBOM.
- [ ] Firma de artefactos.
- [ ] Release notes.
- [ ] Migraciones.
- [ ] Canal beta.
- [ ] Canal stable.

## Comunidad

- [ ] Guía de contribución.
- [ ] Issue templates.
- [ ] PR template.
- [ ] CODEOWNERS.
- [ ] Documentación de plugins.
- [ ] Roadmap público.
- [ ] Inventario de assets.
- [ ] Política de seguridad.

---

# 15. Backlog priorizado

## P0 — Bloqueante

- [ ] Repositorio y licencia.
- [ ] Modelo de dominio.
- [ ] Memoria CRUD.
- [ ] Recordatorio puntual.
- [ ] Recurrencia.
- [ ] Zona horaria.
- [ ] Scheduler.
- [ ] Idempotencia.
- [ ] Notificación local.
- [ ] Exportación.
- [ ] Heurística.
- [ ] Healthchecks.
- [ ] CI.

## P1 — MVP público

- [ ] Grafo limitado.
- [ ] Búsqueda híbrida.
- [ ] PostgreSQL.
- [ ] Redis.
- [ ] Worker.
- [ ] Docker.
- [ ] LLM Router.
- [ ] PWA.
- [ ] Demo GitHub Pages.
- [ ] Logs y auditoría.

## P2 — Beta multiplataforma

- [ ] APK.
- [ ] Desktop.
- [ ] CLI.
- [ ] Audio.
- [ ] Embeddings locales.
- [ ] Mascotas por agente.
- [ ] MCP interno.
- [ ] Graphify read-only.

## P3 — Plataforma extensible

- [ ] MCP externo completo.
- [ ] Skills.
- [ ] Agentes personalizados.
- [ ] Google Calendar.
- [ ] Telegram.
- [ ] Gmail borradores.
- [ ] Sincronización.
- [ ] Workspaces compartidos.

## P4 — Escala y comunidad

- [ ] Marketplace de skills.
- [ ] Plugin SDK.
- [ ] Observabilidad avanzada.
- [ ] Kubernetes.
- [ ] Multi-región.
- [ ] Agentes coordinados.

---

# 16. Milestones

## M0 — Repositorio listo

**Salida:** estructura, licencia, CI, documentación y ADRs.

## M1 — Demo pública

**Salida:** GitHub Pages navegable con chat, panel y grafo mock.

## M2 — Local usable

**Salida:** memoria y recordatorios offline.

## M3 — Servidor privado

**Salida:** Docker con API, database, worker y scheduler.

## M4 — Inteligencia controlada

**Salida:** LLM Router, structured outputs y búsqueda semántica.

## M5 — Multiplataforma

**Salida:** APK y desktop instalables.

## M6 — Grafo real

**Salida:** relaciones, procedencia, filtros y exportación.

## M7 — MCP seguro

**Salida:** gateway, scopes, Graphify opcional y auditoría.

## M8 — Agentes

**Salida:** skills, mascotas y autonomía limitada.

## M9 — Integraciones

**Salida:** calendario, Telegram y correo limitado.

## M10 — Release estable

**Salida:** seguridad, performance, backups, SBOM y documentación.

---

# 17. Plan de branches y trabajo GitHub

## Branches

```text
main       → estable
next       → integración de próxima versión
feature/*  → funcionalidad
fix/*      → corrección
security/* → corrección sensible
release/*  → preparación de release
```

## Pull request

Cada PR debe incluir:

- Problema.
- Solución.
- Archivos afectados.
- Tests.
- Capturas si modifica UI.
- Migración si modifica datos.
- Cambios de seguridad.
- Impacto en compatibilidad.

## CI mínima

- Lint.
- Type check.
- Unit tests.
- Integration tests.
- Build web.
- Build API.
- SAST.
- Secret scan.
- Dependency audit.

---

# 18. Gestión de assets visuales

## Repositorio

```text
assets/
├── mascot/
├── agents/
├── sprites/
├── hud/
├── icons/
├── palettes/
├── source/
└── licenses/
```

## Pipeline

```text
Generación conceptual
→ selección
→ limpieza manual
→ palette lock
→ sprite sheet
→ revisión UI
→ optimización
→ inventario
→ release
```

## Reglas

- No incluir watermarks.
- No utilizar assets de stock sin licencia.
- Guardar origen y modelo utilizado.
- Registrar licencia.
- Probar en 16/32/64/128 px.
- Mantener escalado nearest-neighbor.

---

# 19. Seguridad durante el desarrollo

- Nunca subir `.env`.
- Ejecutar Gitleaks en cada PR.
- No usar datos reales en fixtures.
- Usar cuentas sandbox para integraciones.
- Rotar tokens de desarrollo.
- No incluir audios reales en tests.
- Mockear proveedores LLM.
- Crear MCP malicioso de prueba.
- Verificar aislamiento entre workspaces.
- Revisar dependencias nuevas.

---

# 20. Definición de hecho

Una tarea no está terminada solo porque funciona localmente. Debe cumplir:

1. Código implementado.
2. Tests.
3. Manejo de error.
4. Estados de loading/offline.
5. Permisos.
6. Auditoría.
7. Documentación.
8. Compatibilidad definida.
9. Migración si aplica.
10. Revisión de seguridad.
11. Capturas o pruebas visuales si aplica.
12. Criterio de rollback.

---

# 21. Pruebas por fase

## Núcleo

- Fecha ambigua.
- Zona horaria.
- Recurrencia.
- Cierre inesperado.
- Borrado.
- Exportación.

## Backend

- Reinicio API.
- Reinicio worker.
- Duplicación de jobs.
- Redis caído.
- Base de datos lenta.
- Delivery fallido.

## IA

- JSON inválido.
- Prompt injection.
- LLM caído.
- Rate limit.
- Fallback heurístico.
- Memoria no autorizada.

## MCP

- Tool timeout.
- Scope insuficiente.
- Servidor malicioso.
- Revocación.
- Respuesta demasiado grande.
- Replay.

## Plataformas

- APK sin permiso.
- Desktop sin conexión.
- PWA offline.
- Escalado pixelado.
- Reduced motion.
- Diferentes tamaños de pantalla.

---

# 22. Criterios de release

## Alpha

- Puede romperse.
- Datos de prueba.
- Sin promesa de compatibilidad.
- Logs ampliados.

## Beta

- Flujo núcleo estable.
- Migraciones.
- Backups.
- Instaladores.
- Reporte de errores.

## Stable

- Suite de pruebas.
- Seguridad revisada.
- Documentación.
- Compatibilidad definida.
- Restore probado.
- Releases firmados o con checksums.

---

# 23. Gestión de riesgos del plan

| Riesgo | Señal temprana | Acción |
|---|---|---|
| Scope excesivo | Muchas features P0 | Congelar alcance |
| Backend monolítico | UI llama directamente a SDKs | Mover a adaptadores |
| Scheduler poco fiable | Duplicados | Idempotencia y locks |
| Coste LLM | Muchas llamadas por chat | Router y presupuesto |
| MCP inseguro | Tools sin scopes | Policy engine obligatorio |
| UI pesada | FPS bajo en móvil | Sprite sheets y fallback |
| Licencias inciertas | Assets sin origen | Retirar y auditar |
| Comunidad bloqueada | PRs difíciles de probar | CI y docs |
| Pérdida de datos | Backups nunca restaurados | Prueba periódica |

---

# 24. Primer sprint recomendado

## Objetivo

Crear la primera rebanada vertical completa:

```text
Chat
→ interpretar recordatorio
→ confirmar
→ guardar
→ programar
→ notificar
→ completar
→ auditar
```

## Tareas

- [ ] Crear repositorio base.
- [ ] Crear modelo Reminder.
- [ ] Crear parser heurístico.
- [ ] Crear endpoint de propuesta.
- [ ] Crear confirmación.
- [ ] Crear SQLite.
- [ ] Crear scheduler local.
- [ ] Crear notificación mock.
- [ ] Crear panel Hoy mínimo.
- [ ] Crear test E2E.
- [ ] Crear estado visual del golem.

## Resultado

No se busca todavía una aplicación completa. Se busca demostrar que el ciclo más importante funciona de punta a punta sin perder datos ni confundir al usuario.

---

# 25. Criterios de aceptación del plan

El plan se considera suficientemente definido cuando:

- Cada módulo tiene una fase.
- Cada fase tiene entregables.
- Cada entregable tiene criterio de salida.
- Las dependencias están identificadas.
- El MVP tiene un backlog P0/P1.
- La distribución está contemplada desde el inicio.
- La seguridad aparece en cada fase.
- La UI y el backend tienen estados compatibles.
- Las tareas asíncronas tienen reintentos.
- La comunidad puede contribuir sin conocer todo el sistema.

---

# 26. Conclusión

VNBOT debe implementarse como una secuencia de productos cada vez más capaces, no como un único lanzamiento gigantesco. La primera versión debe probar la confiabilidad del núcleo: capturar, estructurar, recordar y notificar.

Después se añaden IA, audio, plataformas, grafo, MCP, agentes e integraciones, siempre con interfaces estables, jobs auditables y permisos visibles.

La estrategia de implementación queda resumida así:

```text
Primero confiabilidad.
Después memoria.
Luego distribución.
Después extensibilidad.
Finalmente autonomía.
```

La autonomía avanzada solo será valiosa si el usuario puede saber qué ocurrió, por qué ocurrió, qué datos se utilizaron y cómo detener o revertir la acción.

---

# 27. MVP comprimido: 0.1 unificado

### Razón

Las fases originales 0.1 (demo), 0.2 (núcleo local) y 0.3 (servidor) pueden fusionarse en un bloque que entregue valor real más rápido.

### Alcance del 0.1 unificado

- Monorepo con CI (lint, typecheck, tests, secret scan).
- Web/PWA con chat.
- Backend embebido o Docker con SQLite.
- Fallback heurístico (sin LLM) documentado y testeado.
- Al menos 1 proveedor LLM configurado.
- Memorias CRUD con búsqueda textual.
- Recordatorios puntuales y recurrentes con scheduler.
- Grafo básico (CRUD de nodos y edges).
- Exportación e importación cifrada.
- Panel de auditoría básico.
- OpenTelemetry tracing en endpoints principales.
- Tests unitarios con 60% cobertura en core.
- axe-core en CI sin violaciones AA críticas.
- Demo estática en GitHub Pages (paralelo, no bloqueante).

### Lo que NO incluye el 0.1

- APK, Desktop nativo, CLI nativo.
- MCP externo.
- Búsqueda semántica (requiere embeddings).
- Múltiples usuarios/workspaces.
- Sincronización multi-dispositivo.
- Audio.
- Agentes personalizables.

### Criterio de salida del 0.1

- Una persona puede: crear una memoria, crear un recordatorio, buscar, exportar e importar — sin servidor externo.
- Los tests pasan en CI.
- El dashboard de observabilidad muestra métricas básicas.
- La documentación está actualizada.

---

# 28. Documentos adicionales de soporte

Los siguientes documentos deben existir antes de la implementación activa:

| Documento | Propósito | Necesario antes de |
|---|---|---|
| 11-ESTRATEGIA-SYNC-VNBOT.md | Diseño de sincronización multi-dispositivo | Fase 0.3 (plataformas) |
| 12-TESTING-Y-OBSERVABILIDAD-VNBOT.md | Estrategia de tests y OpenTelemetry | Fase 0.1 (inicio de código) |
| 13-GOBERNANZA-DE-PROYECTO-VNBOT.md | Modelo de gobernanza y contribución | Fase 0 (preparación repo) |
