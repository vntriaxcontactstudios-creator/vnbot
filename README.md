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
├── vendor/                        # Repos externos como lógica base (snapshots)
│   ├── web/firecrawl/             # Scraping web estructurado
│   ├── voice/pipecat/             # Voz en tiempo real
│   ├── voice/whisper/             # Transcripción de audio
│   ├── video/yt-dlp/              # Descarga de video/audio
│   ├── search/duckduckgo_search/  # Búsqueda web sin API key
│   ├── embeddings/sentence-transformers/  # Embeddings locales
│   ├── security/rebuff/           # Defensa contra prompt injection
│   └── README.md                  # Índice y docs de integración
│
├── skills/                        # Catálogo de skills planificadas
│   ├── ciencias/                  # Math, physics, chemistry, stats
│   ├── planificacion/             # Schedule, tasks, goals, decisions
│   ├── trading/                   # Market lookup, technical analysis (read-only)
│   ├── documentos/                # PDF, OCR, Word, Markdown, translate
│   ├── storytelling/              # Plot, characters, dialogue, outline
│   ├── ideacion/                  # Brainstorm, mindmap, SCAMPER
│   ├── analisis/                  # Deep analysis, sentiment, network, trends
│   ├── referencia/                # Wikipedia, dictionary, currency, code
│   └── README.md                  # Catálogo completo (38 skills)
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

## Integraciones incluidas (vendor/)

Repositorios externos clonados como lógica base para el MVP:

| Capability | Repo | Ubicación |
|-----------|------|-----------|
| Web scraping | [firecrawl](https://github.com/mendableai/firecrawl) | `vendor/web/firecrawl/` |
| Voz bidireccional | [pipecat](https://github.com/pipecat-ai/pipecat) | `vendor/voice/pipecat/` |
| Transcripción audio | [whisper](https://github.com/openai/whisper) | `vendor/voice/whisper/` |
| Descarga video/audio | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | `vendor/video/yt-dlp/` |
| Búsqueda web | [duckduckgo_search](https://github.com/deedy5/duckduckgo_search) | `vendor/search/duckduckgo_search/` |
| Embeddings locales | [sentence-transformers](https://github.com/UKPLab/sentence-transformers) | `vendor/embeddings/sentence-transformers/` |
| Prompt injection defense | [rebuff](https://github.com/protectai/rebuff) | `vendor/security/rebuff/` |

Ver [`vendor/README.md`](./vendor/README.md) para detalles de integración de cada repo.

## Skills planificadas (skills/)

38 skills organizadas en 8 categorías:

| Categoría | Skills | Descripción |
|-----------|--------|-------------|
| `ciencias/` | 5 | Math, physics, chemistry, statistics |
| `planificacion/` | 5 | Schedule, tasks, goals, decisions, pomodoro |
| `trading/` | 4 | Market lookup, technical analysis (read-only, NO execution) |
| `documentos/` | 6 | PDF, OCR, Word, Markdown, translate |
| `storytelling/` | 5 | Plot, characters, dialogue, outline, continue |
| `ideacion/` | 5 | Brainstorm divergent/convergent, mindmap, SCAMPER |
| `analisis/` | 6 | Deep analysis, sentiment, network, trends, risk |
| `referencia/` | 6 | Wikipedia, dictionary, currency, timezone, code, recipes |

Ver [`skills/README.md`](./skills/README.md) para el catálogo completo con repos de referencia, riesgo y autonomía por skill.

## Integraciones futuras (post-MVP)

- **posthog/py-recapture** — Screenshots de páginas
- **rhasspy/wyoming-piper** — TTS local offline
- **NVIDIA/NeMo-Guardrails** — Guardrails completos
- **meta-llama/llama-guard** — Clasificador de contenido unsafe
- **microsoft/presidio** — PII detection/redaction
- **temporalio/temporal-python** — Workflows durables
- **langchain-ai/langgraph** — State machines para loops de agentes
- **searxng/searxng** — Metabuscador self-hosteable

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
