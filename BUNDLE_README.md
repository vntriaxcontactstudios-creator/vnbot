# VNBOT

> Memoria personal open source, recordatorios confiables y mini-agentes bajo el control del usuario.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Status: Planning](https://img.shields.io/badge/status-planning-blue.svg)](./docs_vnbot/README-DOCUMENTACION.md)

VNBOT es un proyecto open source para crear un asistente personal privado, autoalojable y extensible. Permite capturar información mediante lenguaje natural, convertirla en memorias, tareas, listas o recordatorios y recuperarla mediante búsqueda, relaciones y agentes especializados.

El proyecto está diseñado para crecer desde una instalación local hasta una plataforma con:

- Web/PWA.
- APK Android.
- Desktop para Windows, Linux y macOS.
- CLI.
- Docker.
- Múltiples proveedores LLM.
- Modelos locales.
- Memoria basada en grafo.
- MCP.
- Skills y mini-agentes.
- Integraciones oficiales.

---

## Principio central

```text
Capturar → Interpretar → Explicar → Confirmar → Ejecutar → Auditar
```

El modelo de IA puede interpretar y proponer, pero el dominio valida, el sistema de permisos autoriza y el backend registra el resultado.

---

## Estado del proyecto

VNBOT se encuentra en fase de definición y preparación del MVP.

Actualmente existe documentación de producto, arquitectura, backend, seguridad, UI/UX, flujo de aplicación, modelo de datos, MCP, skills, sincronización, testing y observabilidad, gobernanza y roadmap. La implementación se desarrollará por fases para mantener el núcleo pequeño, portable y verificable.

---

## Funcionalidades previstas

### Núcleo

- Chat en lenguaje natural.
- Recordatorios puntuales y recurrentes.
- Zona horaria explícita.
- Memoria personal editable.
- Nodos y relaciones.
- Grafo visual limitado.
- Búsqueda textual y semántica.
- Listas.
- Exportación e importación.
- Auditoría de acciones.

### Inteligencia

- Múltiples LLM.
- Ollama y modelos locales.
- Fallback heurístico.
- Structured outputs.
- Skills versionadas.
- Agentes personalizados.
- Mascota diferente por agente.

### Integraciones

- MCP.
- Graphify como integración opcional.
- Calendarios.
- Telegram.
- Email mediante lectura/borradores.
- WhatsApp Business API en una fase posterior.

### Distribución

- GitHub Pages para demo y documentación.
- GitHub Releases para APK y desktop.
- Docker para servidores.
- CLI para terminal.

---

## Privacidad

VNBOT contempla tres modos:

1. **Local Estricto:** datos, audio, embeddings y LLM local en el dispositivo.
2. **Servidor Privado:** instalación propia con API, base de datos y workers.
3. **LLM Externo:** proveedor seleccionado por el usuario, con contexto mínimo y política visible.

La documentación no utiliza “zero-knowledge” como promesa genérica. Se especifica en cada modo dónde se cifra, dónde se descifra y qué componentes pueden leer el contenido.

---

## Dirección visual

VNBOT utilizará una estética propia de:

- Pixel art de alta calidad.
- Golem informático como mascota.
- Variantes visuales por agente.
- HUD cyberpunk modular.
- Paneles con bordes angulares.
- Sprite sheets.
- Estados emocionales ligados a procesos reales.

No se utilizará glassmorphism ni blur como lenguaje principal. La interfaz priorizará legibilidad, accesibilidad y rendimiento en dispositivos móviles.

---

## Arquitectura resumida

```text
Web/PWA · APK · Desktop · CLI
              ↓
API versionada
              ↓
Dominio: memoria · grafo · recordatorios · agentes
              ↓
Workers · scheduler · cache · storage
              ↓
LLM Router · Skills · Policy Engine
              ↓
MCP Gateway e integraciones oficiales
```

Persistencia prevista:

- IndexedDB para PWA.
- SQLite para local y desktop.
- PostgreSQL para servidor.
- Redis para colas, locks, cache y rate limiting.
- MinIO/S3 para archivos y backups.

---

## Inicio rápido de documentación

La documentación completa está en [`docs_vnbot/`](./docs_vnbot/).

- [Documento Maestro](./docs_vnbot/00-DOCUMENTO-MAESTRO-VNBOT.md)
- [PRD](./docs_vnbot/01-PRD-VNBOT.md)
- [TRD](./docs_vnbot/02-TRD-VNBOT.md)
- [Esquema Backend](./docs_vnbot/03-ESQUEMA-BACKEND-VNBOT.md)
- [Plan de Implementación](./docs_vnbot/04-PLAN-IMPLEMENTACION-VNBOT.md)
- [Diseño UI/UX](./docs_vnbot/05-DISENO-UI-UX-VNBOT.md)
- [App Flow](./docs_vnbot/06-APP-FLOW-VNBOT.md)
- [Modelo de Datos](./docs_vnbot/07-MODELO-DATOS-VNBOT.md)
- [Seguridad y Privacidad](./docs_vnbot/08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md)
- [MCP y Skills](./docs_vnbot/09-MCP-Y-SKILLS-VNBOT.md)
- [Roadmap](./docs_vnbot/10-ROADMAP-VNBOT.md)
- [Estrategia de Sync](./docs_vnbot/11-ESTRATEGIA-SYNC-VNBOT.md)
- [Testing y Observabilidad](./docs_vnbot/12-TESTING-Y-OBSERVABILIDAD-VNBOT.md)
- [Gobernanza de Proyecto](./docs_vnbot/13-GOBERNANZA-DE-PROYECTO-VNBOT.md)
- [Índice de documentación](./docs_vnbot/README-DOCUMENTACION.md)

---

## Roadmap resumido

```text
0.1  MVP funcional (Web/PWA + Docker + fallback heurístico)
0.2  Servidor privado y estabilización
0.3  Plataformas (APK, Desktop, CLI) — requiere sync probada
0.4  Memoria grafo avanzada
0.5  MCP Gateway
0.6  Skills y agentes
0.7  Integraciones oficiales
0.8  Estabilización
0.9  Testing y seguridad
1.0  Release estable
```

La autonomía avanzada se implementará después de que memoria, recordatorios, jobs y auditoría sean confiables.

---

## Desarrollo futuro

La estructura prevista del repositorio es:

```text
apps/
  web/
  desktop/
  android/
  cli/
services/
  api/
  worker/
  scheduler/
  mcp-gateway/
packages/
  domain/
  schemas/
  ui/
  connectors/
skills/
docs/
infra/
assets/
tests/
```

Cada integración nueva debe ser un adaptador o plugin cuando sea posible. El núcleo no debe depender de una integración externa concreta.

---

## Testing, observabilidad y accesibilidad

VNBOT implementa tests y observabilidad desde la primera línea de código:

- **Testing:** pirámide de tests (unit → integration → e2e) con cobertura mínima por módulo.
- **Observabilidad:** OpenTelemetry para tracing, métricas y logs estructurados.
- **Accesibilidad:** WCAG 2.2 AA como mínimo, con auditorías automatizadas en CI.
- **Benchmarks:** métricas de rendimiento del grafo y recordatorios en cada release.

---

## Gobernanza

VNBOT tiene un modelo de gobernanza definido con roles (maintainers, contributors), procesos de decisión (rutinarios, técnicos, estratégicos), ADRs y un proceso de contribución estructurado. Ver [Gobernanza de Proyecto](./docs_vnbot/13-GOBERNANZA-DE-PROYECTO-VNBOT.md).

---

## Contribuir

Durante la fase de preparación, las contribuciones más útiles serán:

- Revisión de documentación.
- Tests.
- Accesibilidad.
- Componentes UI.
- Traducciones.
- Auditoría de dependencias.
- Diseño de skills.
- Adaptadores de proveedores.

Antes de contribuir, consulta:

- `CONTRIBUTING.md`.
- `SECURITY.md`.
- `THIRD_PARTY_NOTICES.md`.
- La documentación correspondiente al módulo.

---

## Licencia

El código fuente de VNBOT se distribuirá bajo la licencia MIT.

Los assets visuales, fuentes, modelos, datasets y dependencias pueden tener licencias diferentes. Cada uno debe registrarse en el inventario de terceros y distribuirse respetando sus condiciones.

---

## Nota de alcance

VNBOT no pretende ser un agente con acceso ilimitado al dispositivo. La plataforma busca permitir capacidades amplias, pero con permisos visibles, scopes, confirmaciones, límites, auditoría y revocación.

> **VNBOT debe ser extensible en capacidades, pero restrictivo en autoridad.**
