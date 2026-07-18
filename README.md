# VNBOT

> Memoria personal open source, recordatorios confiables y mini-agentes bajo el control del usuario.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Status: Planning](https://img.shields.io/badge/status-planning-blue.svg)](./docs/00-DOCUMENTO-MAESTRO-VNBOT.md)

VNBOT es un proyecto open source para crear un asistente personal privado, autoalojable y extensible. Permite capturar información mediante lenguaje natural, convertirla en memorias, tareas, listas o recordatorios y recuperarla mediante búsqueda, relaciones y agentes especializados.

## Principio central

```text
Capturar → Interpretar → Explicar → Confirmar → Ejecutar → Auditar
```

El modelo de IA puede interpretar y proponer, pero el dominio valida, el sistema de permisos autoriza y el backend registra el resultado.

## Estructura del repositorio

```
vnbot/
├── docs/                          # 14 documentos MD (00-13)
│   ├── 00-DOCUMENTO-MAESTRO-VNBOT.md
│   ├── 01-PRD-VNBOT.md
│   ├── 02-TRD-VNBOT.md
│   ├── 03-ESQUEMA-BACKEND-VNBOT.md
│   ├── 04-PLAN-IMPLEMENTACION-VNBOT.md
│   ├── 05-DISENO-UI-UX-VNBOT.md
│   ├── 06-APP-FLOW-VNBOT.md
│   ├── 07-MODELO-DATOS-VNBOT.md
│   ├── 08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md
│   ├── 09-MCP-Y-SKILLS-VNBOT.md
│   ├── 10-ROADMAP-VNBOT.md
│   ├── 11-ESTRATEGIA-SYNC-VNBOT.md
│   ├── 12-TESTING-Y-OBSERVABILIDAD-VNBOT.md
│   └── 13-GOBERNANZA-DE-PROYECTO-VNBOT.md
│
├── deliverables/                  # Documentos finales entregables
│   ├── pdf/                       # 7 PDFs (PRD, TRD, Backend, Plan, Vol I-III)
│   └── pptx/                      # PPTX (regenerables desde source/html-slides/)
│
├── source/                        # Fuentes para regeneración
│   ├── html-slides/               # 96 HTML slides + CSS
│   │   ├── uiux-design-system/    # 39 slides
│   │   └── app-flow/              # 57 slides
│   └── generation-scripts/        # Python + HTML covers para PDFs
│
├── assets/                        # Assets visuales
│   ├── references/                # 5 imágenes de referencia
│   └── spritesheets/              # 5 spritesheets generados de VNBOT
│
├── prototype-reference/           # Prototipo de referencia
│   └── MINBOT-TASK-DOC.md
│
├── WORKLOG.md                     # Log completo de trabajo
├── BUNDLE_README.md               # README del bundle original
├── CONTENTS.md                    # Índice del bundle
├── VISUAL_REFERENCES_AND_ANALYSIS.md
├── VNBOT_SPRITESHEET_REFERENCE.md
└── README.md                      # Este archivo
```

## Documentación principal

| Documento | Cobertura |
|-----------|-----------|
| [PRD](./docs/01-PRD-VNBOT.md) | Definición de producto, requisitos y criterios |
| [TRD](./docs/02-TRD-VNBOT.md) | Arquitectura técnica, stack y criterios operativos |
| [Esquema Backend](./docs/03-ESQUEMA-BACKEND-VNBOT.md) | Servicios, API, jobs, scheduler, MCP |
| [Plan Implementación](./docs/04-PLAN-IMPLEMENTACION-VNBOT.md) | Fases, milestones, backlog |
| [Diseño UI/UX](./docs/05-DISENO-UI-UX-VNBOT.md) | Interfaz, mascotas y sistema visual |
| [App Flow](./docs/06-APP-FLOW-VNBOT.md) | Flujos de usuario y estados |
| [Modelo de Datos](./docs/07-MODELO-DATOS-VNBOT.md) | Entidades, relaciones, persistencia |
| [Seguridad](./docs/08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md) | Amenazas, criptografía, privacidad |
| [MCP y Skills](./docs/09-MCP-Y-SKILLS-VNBOT.md) | Tools, scopes, agentes |
| [Roadmap](./docs/10-ROADMAP-VNBOT.md) | Fases 0.1→1.0 |
| [Estrategia Sync](./docs/11-ESTRATEGIA-SYNC-VNBOT.md) | Sincronización multi-dispositivo |
| [Testing y Observabilidad](./docs/12-TESTING-Y-OBSERVABILIDAD-VNBOT.md) | Calidad y OpenTelemetry |
| [Gobernanza](./docs/13-GOBERNANZA-DE-PROYECTO-VNBOT.md) | Roles, decisiones, ADRs |

## Deliverables finales

### PDFs (7 documentos)
- `VNBOT_PRD.pdf` — Definición de producto
- `VNBOT_TRD.pdf` — Arquitectura técnica
- `VNBOT_ESQUEMA_BACKEND.pdf` — Backend detallado
- `VNBOT_PLAN_IMPLEMENTACION.pdf` — Plan ejecutable
- `VNBOT_VOL1_DATOS_SEGURIDAD_EXTENSIBILIDAD.pdf` — Modelo datos + Seguridad + MCP/Skills
- `VNBOT_VOL2_ROADMAP_SYNC.pdf` — Roadmap + Estrategia Sync
- `VNBOT_VOL3_TESTING_GOBERNANZA.pdf` — Testing + Gobernanza

### PPTX (regenerables)
- `VNBOT_UIUX_DESIGN_SYSTEM.pptx` — 39 slides
- `VNBOT_APP_FLOW.pptx` — 57 slides

## Stack previsto

- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** Python 3.12 + FastAPI + Pydantic v2 + SQLAlchemy 2
- **DB:** SQLite (local) / PostgreSQL + pgvector (server)
- **Cola:** Redis + Dramatiq
- **LLM:** Ollama (local) + OpenAI/Anthropic (externo) con router y fallback
- **MCP:** Gateway con policy engine
- **Observabilidad:** OpenTelemetry
- **Distribución:** Docker + GitHub Releases + GitHub Pages (demo)

## Roadmap resumido

```text
0.1 Demo · 0.2 Local · 0.3 Server · 0.4 Plataformas · 0.5 Memoria
0.6 MCP · 0.7 Agentes · 0.8 Integraciones · 0.9 Estabilización · 1.0 Stable
```

## Integraciones futuras planificadas

- **Firecrawl** — Web scraping estructurado
- **Pipecat** — Voz en tiempo real
- **yt-dlp + FFmpeg** — Procesamiento de video/audio
- **Whisper** — Transcripción local
- **SearXNG / DuckDuckGo** — Búsqueda web
- **NeMo Guardrails** — Defensa contra prompt injection
- **LangGraph** — Loops de agentes autónomos

## Contribuir

Durante la fase de preparación, las contribuciones más útiles serán:
- Revisión de documentación
- Tests
- Accesibilidad
- Componentes UI
- Traducciones
- Auditoría de dependencias

Ver [Gobernanza](./docs/13-GOBERNANZA-DE-PROYECTO-VNBOT.md) para el modelo de contribución.

## Licencia

Código bajo MIT. Assets visuales, fuentes, modelos y dependencias pueden tener licencias diferentes.

## Estado

Fase de preparación del MVP. La documentación está completa; la implementación se desarrollará por fases según el [Plan de Implementación](./docs/04-PLAN-IMPLEMENTACION-VNBOT.md).
