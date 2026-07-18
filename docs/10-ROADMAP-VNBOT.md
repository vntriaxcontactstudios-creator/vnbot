# VNBOT — Roadmap de producto y desarrollo

> **Documento:** Roadmap
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Plan de evolución
> **Fecha:** 2026-07-16
> **Documentos relacionados:** [PRD](./01-PRD-VNBOT.md), [TRD](./02-TRD-VNBOT.md), [Plan de Implementación](./04-PLAN-IMPLEMENTACION-VNBOT.md)

---

# 1. Propósito

Este roadmap define cómo VNBOT evolucionará desde una demostración pública hasta una plataforma open source de memoria personal, recordatorios y mini-agentes.

El roadmap no debe interpretarse como una promesa de fechas rígidas. Define prioridades, dependencias y condiciones de salida. Las funciones se incorporan cuando el núcleo anterior es confiable, no simplemente porque sean atractivas o técnicamente posibles.

La prioridad estratégica es:

```text
Confiabilidad
→ privacidad
→ memoria
→ distribución
→ extensibilidad
→ integraciones
→ autonomía
```

---

# 2. Principios del roadmap

## 2.1. Publicar pronto, pero no publicar inseguro

La demo de GitHub Pages puede publicarse temprano porque no procesa datos reales. Las funciones con memoria real, audio, archivos e integraciones deben pasar por controles adicionales.

## 2.2. Cada release debe ser utilizable

Una release no debe ser solo una colección de commits. Cada versión debe resolver un flujo concreto y tener:

- Documentación.
- Instalación.
- Pruebas.
- Notas de cambios.
- Migraciones.
- Criterios de rollback.

## 2.3. El núcleo no depende de integraciones

Las integraciones externas se añaden como adaptadores. Si Google Calendar, Telegram, Graphify o un proveedor LLM falla, la memoria y los recordatorios internos deben continuar funcionando.

## 2.4. Primero acciones internas, después externas

La creación de una memoria o recordatorio propio es menos riesgosa que enviar un correo o modificar un calendario externo. La autonomía se incrementa por niveles.

## 2.5. La comunidad debe poder contribuir por módulos

El proyecto debe permitir contribuciones independientes en:

- Frontend.
- UI pixel art.
- Skills.
- Integraciones.
- Documentación.
- Localización.
- Seguridad.
- Modelos y adapters.

---

# 3. Estado actual

## Completado en documentación

- PRD.
- TRD.
- Esquema Backend.
- Plan de Implementación.
- Diseño UI/UX.
- App Flow.
- Modelo de Datos.
- Seguridad y Privacidad.
- MCP y Skills.
- Roadmap.
- Documento Maestro.

## Prototipos visuales existentes

- Golem informático principal y variantes.
- Hoja conceptual de estados de animación.
- Referencias de HUD cyberpunk.
- Dirección visual pixel art definida.

## Pendiente de implementación

- Monorepo funcional.
- Demo navegable.
- Núcleo local.
- Backend real.
- Scheduler y workers.
- APK y desktop.
- MCP Gateway.
- Skills ejecutables.

---

# 4. Versionado

## Semantic Versioning

```text
MAJOR.MINOR.PATCH
```

- `MAJOR`: cambios incompatibles de API, exportación o configuración.
- `MINOR`: nuevas funciones compatibles.
- `PATCH`: correcciones y mejoras compatibles.

## Canales

```text
nightly  → builds automáticos para desarrollo
alpha    → funciones incompletas para pruebas técnicas
beta     → flujo de usuario estable, posibles cambios menores
stable   → release recomendada
```

## Etiquetas

```text
v0.1.0-demo
v0.2.0-local
v0.3.0-server
v0.4.0-platforms
v0.4.5-sync
v0.5.0-memory
v0.6.0-mcp
v0.7.0-agents
v0.8.0-integrations
v0.9.0-stabilization
v0.9.5-testing
v1.0.0-stable
```

---

# 5. Fase 0 — Preparación del repositorio

## Objetivo

Crear una base legal, técnica y comunitaria antes de añadir funcionalidades.

## Entregables

- Repositorio público.
- MIT License.
- README.
- SECURITY.md.
- CONTRIBUTING.md.
- CODE_OF_CONDUCT.md.
- CHANGELOG.md.
- Inventario de dependencias.
- Inventario de assets.
- CI inicial.
- ADRs.

## Tareas

- [ ] Crear monorepo.
- [ ] Definir nombre oficial VNBOT.
- [ ] Migrar nombre histórico MinBot-Task.
- [ ] Configurar ramas.
- [ ] Configurar protección de `main`.
- [ ] Añadir linter y formatter.
- [ ] Añadir tests.
- [ ] Añadir Gitleaks.
- [ ] Añadir Semgrep.
- [ ] Añadir Dependabot/Renovate.
- [ ] Crear guía de contribución.

## Criterio de salida

Una persona externa puede clonar, entender la estructura, ejecutar la validación y crear un Pull Request siguiendo instrucciones públicas.

---

# 5.5. Revisión de alcance: MVP comprimido

## Razón

Las fases originales 0.1 (demo estática), 0.2 (núcleo local) y 0.3 (servidor Docker) pueden abordarse como un bloque unificado para reducir el tiempo hasta un producto utilizable. La demo estática no debe bloquear el código funcional.

## Enfoque recomendado

```text
0.1  MVP funcional (Web/PWA + Docker)
     - Chat con 1 proveedor LLM + fallback heurístico
     - Memorias CRUD + búsqueda textual
     - Recordatorios puntuales y recurrentes
     - Grafo básico
     - Exportación/importación
     - Auditoría
     - Demo estática en GitHub Pages (paralelo, no bloqueante)
     ↓
0.2  Servidor privado y estabilización
     - Multiusuario y workspaces
     - Redis, workers, scheduler robusto
     - Búsqueda semántica
     ↓
0.3  Plataformas (APK, Desktop, CLI)
     - Requiere sync strategy probada (ver documento 11)
     ↓
0.4  Memoria grafo avanzada
0.5  MCP Gateway
0.6  Skills y agentes
0.7  Integraciones oficiales
0.8  Estabilización
0.9  Testing y seguridad
1.0  Release estable
```

## Impacto

- El usuario tiene algo funcional antes.
- La demo y el producto comparten componentes UI.
- La sync strategy se diseña antes de multiplataforma.
- Testing y observabilidad son cross-cutting desde 0.1.

---

# 6. VNBOT 0.1 — Demo pública en GitHub Pages

## Objetivo

Presentar visualmente VNBOT sin requerir instalación, cuenta ni proveedor de IA.

## Funciones

- Landing.
- Golem principal.
- Chat simulado.
- Crear recordatorio ficticio.
- Vista Hoy ficticia.
- Grafo de ejemplo.
- Selector de agentes.
- Estados emocionales.
- Presentación de Docker, APK y desktop como próximos canales.
- Documentación enlazada.

## Restricciones

- No usar datos reales.
- No pedir API keys.
- No afirmar que se ejecutó una acción externa.
- Mostrar etiquetas “Demo simulada”.
- No depender de backend.

## Criterios de salida

- Carga desde GitHub Pages.
- Funciona en móvil y desktop.
- Tiene fallback sin JavaScript crítico cuando sea posible.
- Incluye accesos a documentación y repositorio.
- La navegación principal se entiende en menos de un minuto.
- Tests unitarios con cobertura mínima del 60% en módulos core.
- OpenTelemetry tracing en endpoints principales.
- axe-core sin violaciones AA críticas.

---

# 7. VNBOT 0.2 — Núcleo local

## Objetivo

Ofrecer una aplicación personal capaz de funcionar sin servidor remoto.

## Funciones

- PWA.
- IndexedDB.
- Bóveda local.
- Chat.
- Heurística.
- Memoria CRUD.
- Grafo básico.
- Recordatorios locales.
- Notificación local cuando la plataforma lo permita.
- Importación/exportación.
- Configuración de zona horaria.

## No incluir todavía

- MCP remoto.
- Envío de email.
- WhatsApp.
- Agente autónomo.
- Audio cloud obligatorio.

## Criterios de salida

- Crear una memoria sin conexión.
- Crear un recordatorio sin LLM.
- Reiniciar y conservar datos.
- Exportar e importar.
- Olvidar una memoria y limpiar índices locales.
- Tests unitarios con cobertura mínima del 60% en módulos core.
- OpenTelemetry tracing en endpoints principales.
- axe-core sin violaciones AA críticas.

---

# 8. VNBOT 0.3 — Servidor privado y Docker

## Objetivo

Permitir que una persona despliegue VNBOT en un servidor propio.

## Componentes

- FastAPI.
- SQLite para instalación sencilla.
- PostgreSQL para servidor.
- Redis.
- Worker.
- Scheduler.
- Healthchecks.
- API `/api/v1`.
- Autenticación.
- Workspaces.
- Backups.

## Distribución

```bash
docker compose -f docker-compose.server.yml up -d
vnbot doctor
vnbot migrate
```

## Criterios de salida

- Reiniciar API sin perder datos.
- Reiniciar worker sin perder jobs.
- Ejecutar backup y restore.
- Ver healthchecks.
- Separar usuarios y workspaces.
- Entregar notificaciones internas de forma idempotente.

---

# 9. VNBOT 0.4 — Plataformas

## Objetivo

Distribuir VNBOT como APK, desktop y CLI.

## APK

- Capacitor.
- Permisos de micrófono.
- Notificaciones locales.
- Estado de red.
- Filesystem seguro.
- APK firmado.

## Desktop

- Tauri.
- SQLite local.
- Notificaciones nativas.
- Auto-lock.
- Instaladores.
- Windows, Linux y macOS según matriz de soporte.

## CLI

```bash
vnbot init
vnbot add "revisar presupuesto"
vnbot search "Daniel"
vnbot reminders list
vnbot backup create
vnbot doctor
```

## GitHub Release

- APK.
- `.exe`/installer.
- AppImage o `.deb`.
- `.dmg`.
- Checksums.
- SBOM.
- Release notes.

## Criterios de salida

- Instalación documentada.
- Versiones identificables.
- Artefactos con checksum.
- Sin API keys incrustadas.
- Pruebas en dispositivos reales.

---

# 10. VNBOT 0.5 — Memoria grafo

## Objetivo

Convertir la memoria básica en un sistema visible de nodos y relaciones.

## Funciones

- MemoryNode.
- MemoryEdge.
- Procedencia.
- Confianza.
- Contradicciones.
- Expiración.
- Búsqueda textual.
- Búsqueda semántica.
- Recorrido de subgrafos.
- Inspector.
- Vista lista.
- Corrección y olvido.
- Exportación del grafo.

## Límites iniciales

- Profundidad 2–3.
- Top-K configurable.
- Máximo visible por consulta.
- Sin cargar toda la bóveda en el navegador.

## Criterios de salida

- Las memorias se pueden relacionar.
- El usuario entiende el origen de una relación.
- Las inferencias se distinguen de hechos confirmados.
- Borrar un nodo invalida sus derivados.

---

# 11. VNBOT 0.6 — MCP Gateway

## Objetivo

Conectar herramientas externas de manera segura y visible.

## Funciones

- Registro de servidores.
- stdio.
- Streamable HTTP.
- Handshake.
- Descubrimiento.
- Scopes.
- Policy engine.
- Confirmaciones.
- Healthchecks.
- Auditoría.
- Revocación.

## Primera integración

Graphify en modo read-only.

## Segunda integración

Calendario con lectura y creación de eventos confirmada.

## No incluir inicialmente

- Escritura arbitraria de filesystem.
- Envío automático de emails.
- Acciones financieras.
- Navegación sin sandbox.

## Criterios de salida

- Un MCP puede conectarse sin conceder acceso completo.
- Tools descubiertas aparecen deshabilitadas hasta revisión.
- Un fallo del MCP no derriba el núcleo.
- Cada llamada queda registrada.

---

# 12. VNBOT 0.7 — Skills y agentes

## Objetivo

Permitir que el usuario cree asistentes especializados.

## Agentes iniciales

- VNBOT Core.
- Archivista.
- Beacon.
- Navigator.
- Forge.
- Sentinel.
- Scout.

## Funciones

- Crear agente.
- Elegir avatar.
- Seleccionar modelo.
- Escribir instrucciones.
- Asignar skills.
- Asignar scopes de memoria.
- Asignar tools.
- Configurar autonomía.
- Configurar presupuesto.
- Simular.
- Pausar.
- Revocar.

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

## Criterios de salida

- Un agente no puede utilizar una tool no autorizada.
- La mascota refleja su estado.
- El usuario puede revisar permisos.
- Una skill puede desactivarse sin borrar automáticamente sus datos.

---

# 13. VNBOT 0.8 — Integraciones oficiales

## Orden recomendado

1. Calendario interno.
2. Google Calendar.
3. Telegram Bot API.
4. Gmail lectura/borradores.
5. Outlook.
6. Discord bot oficial.
7. WhatsApp Business Cloud API.

## Requisitos por integración

- Documentar API oficial.
- Solicitar scopes mínimos.
- Mostrar datos leídos/escritos.
- Implementar healthcheck.
- Implementar revocación.
- Añadir reintentos.
- Respetar límites.
- Documentar ToS y costes.
- Crear sandbox/mocks.

## Criterios de salida

Una integración puede activarse, desactivarse, reconectarse, auditarse y fallar sin romper memoria ni recordatorios internos.

---

# 14. VNBOT 0.9 — Estabilización

## Seguridad

- Threat model revisado.
- Pentest básico.
- SAST/DAST.
- Escaneo de secretos.
- Dependencias auditadas.
- Revisión MCP.
- Revisión de backups.
- Responsible disclosure.

## Rendimiento

- Pruebas con 10.000 memorias.
- Pruebas con 1.000 recordatorios.
- Pruebas de workers.
- Pruebas de sincronización.
- Pruebas de grafo.
- Pruebas Android de gama baja.
- Pruebas desktop.

## Comunidad

- Plugin SDK inicial.
- Documentación de contribución.
- Issue templates.
- Código de conducta.
- Guías de assets.
- Guía de localización.

---

# 15. VNBOT 1.0 — Release estable

## Requisitos

- API versionada.
- Migraciones documentadas.
- Backups/restores probados.
- Release web estable.
- APK estable.
- Desktop estable.
- Docker estable.
- CLI estable.
- Seguridad revisada.
- UI accesible.
- Exportación portable.
- Sistema de skills documentado.
- MCP con scopes y auditoría.
- Guía de administración.
- Guía de privacidad.

## No significa

VNBOT 1.0 no significa que exista autonomía ilimitada ni todas las integraciones posibles. Significa que el núcleo es confiable, documentado y estable para ampliarse.

---

# 16. Roadmap funcional por áreas

## Memoria

```text
MVP: CRUD y búsqueda
0.5: grafo y procedencia
0.7: scopes por agente
1.0: consolidación, conflictos y exportación madura
```

## Recordatorios

```text
MVP: puntual/recurrente
0.3: workers y scheduler distribuido
0.4: APK/desktop
0.8: calendario y canales externos
1.0: métricas de entrega y resiliencia
```

## IA

```text
MVP: heurística
0.3: proveedor local/externo
0.4: router y structured output
0.7: agentes
1.0: evaluación y optimización de coste
```

## Visual

```text
0.1: landing y mascotas
0.2: panel y chat
0.5: grafo
0.7: mascotas por agente
1.0: packs y sistema de assets estable
```

## MCP

```text
0.6: gateway y tools internas
0.6: Graphify read-only
0.8: integraciones oficiales
1.0: SDK y plugins
```

---

# 17. Matriz de prioridad

| Funcionalidad | Valor | Riesgo | Dependencia | Prioridad |
|---|---:|---:|---|---|
| Fallback heurístico | Alto | Bajo | Ninguna | P0 |
| Testing unitario | Alto | Bajo | Framework | P0 |
| Observabilidad (tracing) | Alto | Bajo | OpenTelemetry | P0 |
| Estrategia de sync | Alto | Alto | Modelo de datos | P1 |
| Accesibilidad WCAG AA | Alto | Medio | Design tokens | P1 |
| Gobernanza de proyecto | Medio | Bajo | Comunidad | P1 |
| Recordatorio puntual | Alto | Bajo | Dominio | P0 |
| Recurrencia | Alto | Medio | Scheduler | P0 |
| Memoria CRUD | Alto | Medio | Storage | P0 |
| Grafo visual | Medio | Bajo | Memoria | P1 |
| LLM Router | Alto | Medio | Chat | P1 |
| Audio local | Alto | Medio | Worker | P1 |
| APK | Alto | Medio | PWA estable | P1 |
| Desktop | Medio | Medio | Storage local | P1 |
| MCP interno | Alto | Alto | Policy engine | P2 |
| Graphify | Medio | Alto | MCP | P2 |
| Email send | Medio | Alto | Integración | P3 |
| WhatsApp | Medio | Alto | API oficial | P3 |
| Marketplace skills | Medio | Alto | Seguridad | P4 |
| Multiagente autónomo | Alto | Muy alto | Todo lo anterior | P4 |

---

# 18. Métricas de release

## Producto

- Tiempo hasta primer recordatorio.
- Porcentaje de onboarding completado.
- Tasa de confirmación correcta.
- Memorias recuperadas correctamente.
- Recordatorios completados.

## Backend

- P95 de API.
- Jobs fallidos.
- Jobs reintentados.
- Duplicados.
- Disponibilidad del scheduler.
- Cache hit rate.

## Seguridad

- Vulnerabilidades abiertas.
- Secret scans fallidos.
- Integraciones con scopes excesivos.
- Incidentes.
- Tiempo de respuesta a reportes.

## Comunidad

- Contribuidores.
- PRs.
- Issues.
- Plugins revisados.
- Descargas.
- Instalaciones Docker.

No se deben recopilar contenidos privados para calcular estas métricas.

---

# 19. Dependencias críticas

```text
Demo
  ↓
Frontend base
  ↓
Modelo de dominio
  ↓
Storage
  ↓
Recordatorios
  ↓
Worker/scheduler
  ↓
LLM/audio
  ↓
Grafo
  ↓
MCP
  ↓
Agentes
  ↓
Integraciones
```

No se debe implementar un agente avanzado sobre un sistema de jobs todavía no confiable.

---

# 20. Release checklist

## Producto

- [ ] Objetivo de release documentado.
- [ ] Funciones fuera de alcance listadas.
- [ ] Criterios de aceptación verificados.

## Código

- [ ] Tests.
- [ ] Lint.
- [ ] Typecheck.
- [ ] Build.
- [ ] Migraciones.

## Seguridad

- [ ] Secret scan.
- [ ] Dependencias.
- [ ] SAST.
- [ ] Permisos.
- [ ] Logs.

## Distribución

- [ ] Artefactos.
- [ ] Checksums.
- [ ] SBOM.
- [ ] Notas.
- [ ] Compatibilidad.

## Documentación

- [ ] README.
- [ ] Guía de instalación.
- [ ] Variables de entorno.
- [ ] Guía de upgrade.
- [ ] Guía de rollback.

## Visual

- [ ] Capturas.
- [ ] Assets licenciados.
- [ ] Reduced motion.
- [ ] Responsive.
- [ ] Accesibilidad.

---

# 21. Riesgos del roadmap

| Riesgo | Consecuencia | Respuesta |
|---|---|---|
| Añadir demasiadas integraciones | Mantenimiento inabarcable | Plugins/adapters |
| Confundir demo con producto | Expectativas incorrectas | Etiquetas claras |
| MCP sin controles | Exposición de datos | Gateway + policy |
| Pixel art pesado | Mala experiencia móvil | Sprite sheets/lazy load |
| LLM costoso | Sostenibilidad baja | Local/fallback/router |
| Scheduler inestable | Recordatorios duplicados | Locks/idempotencia |
| Licencias dudosas | Riesgo legal | Inventario/auditoría |
| Scope creep | Release interminable | P0/P1 congelado |
| Poca documentación | Comunidad bloqueada | Docs por módulo |
| Sync sin diseñar | Pérdida de datos multi-dispositivo | Doc 11 antes de 0.3 |
| Testing insuficiente | Regresiones silenciosas | Cobertura mínima por módulo |
| Accesibilidad postergada | Exclusión de usuarios | WCAG AA desde 0.1 |
| Sin gobernanza clara | Bloqueo de decisiones | Doc 13 en fase 0 |

---

# 21.5. Preocupaciones transversales

Las siguientes áreas no son fases sino requisitos que aplican a todo el desarrollo:

## Testing

VNBOT debe tener tests desde la primera línea de código. Ver [Testing y Observabilidad](./12-TESTING-Y-OBSERVABILIDAD-VNBOT.md).

- Unit tests: mínimos por módulo.
- Integration tests: flujos críticos (chat → memoria, recordatorio → notificación).
- E2E tests: recorrido principal por plataforma.
- Contract tests: MCP tools y API endpoints.

## Observabilidad

- OpenTelemetry para tracing distribuido.
- Logs estructurados (JSON).
- Métricas por módulo (latencia P95, error rate, throughput).
- Dashboards por release.

## Accesibilidad

- WCAG 2.2 AA obligatorio.
- axe-core en CI.
- Auditoría manual por release.
- Testing con screen reader antes de v1.0.

## Documentación

- Cada módulo tiene su propio doc.
- ADRs para decisiones arquitectónicas.
- CHANGELOG por release.
- Guías de contribución y gobernanza.

---

# 22. Roadmap comunitario

## Contribuciones tempranas

- Correcciones de documentación.
- Traducciones.
- Tests.
- Componentes UI.
- Fixtures.
- Accesibilidad.
- Themes.
- Sprites.

## Contribuciones intermedias

- Adapters de storage.
- Proveedores LLM.
- Integraciones oficiales.
- Skills.
- Notificaciones.
- Plugins MCP.

## Contribuciones avanzadas

- Sincronización.
- Graph RAG.
- Workers distribuidos.
- Android nativo.
- Observabilidad.
- Seguridad.

Todas las contribuciones deben cumplir licencia, tests y revisión de seguridad cuando afecten datos o herramientas.

---

# 23. Conclusión

VNBOT crecerá en capas. La primera versión no intentará resolver todas las tareas del usuario, sino demostrar una memoria personal y un sistema de recordatorios fiables, privados y extensibles.

La evolución recomendada es:

```text
0.1 Demo
0.2 Local
0.3 Server
0.4 Plataformas
0.5 Memoria
0.6 MCP
0.7 Agentes
0.8 Integraciones
0.9 Estabilización
1.0 Release estable
```

La regla final del roadmap es:

> **No se añade autonomía a una base que todavía no puede explicar, auditar y recuperar sus propias acciones.**
