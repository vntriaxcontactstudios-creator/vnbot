# VNBOT

> Memoria personal open source, recordatorios confiables y mini-agentes bajo el control del usuario.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Status: MVP Phase 0.1](https://img.shields.io/badge/status-MVP%20Phase%200.1-cyan.svg)](./docs/)

VNBOT es un asistente personal privado, autoalojable y extensible. Convierte texto, voz, imágenes y enlaces en memoria, recordatorios, listas, eventos y acciones controladas.

## Principio central

```text
Capturar → Interpretar → Explicar → Confirmar → Ejecutar → Auditar
```

El modelo de IA puede interpretar y proponer, pero el dominio valida, el sistema de permisos autoriza y el backend registra el resultado.

## Estado del proyecto

**Fase 0.7 — Hermes Learning Loop activo** ✨

- ✅ Fase 0.1: MVP comprimido (chat → proposal → confirm → reminder/memory)
- ✅ Fase 0.2: PostgreSQL dual-mode + Docker Compose
- ✅ Fase 0.4: LLM integration (Z.AI glm-4.6 + heuristic fallback ADR-0007)
- ✅ Fase 0.5: FileReader Registry (106 extensiones) + VLM (glm-4.6v)
- ✅ Fase 0.6: Background review branch (Hermes Track 1)
- ✅ **Fase 0.7: Self-learning loop + skill creation + memory curation** (Hermes Track 2+3)

Documentación completa en [`docs/`](./docs/) y ADRs en [`docs/adrs/`](./docs/adrs/).


## Stack tecnológico

- **Frontend:** React 19 + Vite + TypeScript strict + Tailwind 4 + TanStack Query + Zustand + Dexie + Atropos.js + anime.js + PWA (Service Worker + manifest)
- **Backend:** Python 3.12 + FastAPI + Pydantic v2 + SQLAlchemy 2 async + Alembic + Uvicorn + APScheduler
- **DB:** SQLite (WAL mode) — PostgreSQL+pgvector en Fase 0.2 (Docker Compose ready)
- **LLM:** Z.AI glm-4.6 (parser) + glm-4.6v (VLM imágenes) — sin API key requerida
- **Hermes:** Background review + memory curation + skill creation (ADR-0009 Fase 0.7)
- **Observabilidad:** OpenTelemetry SDK desde día 1
- **Testing:** Vitest + pytest + Playwright + axe-core
- **CI:** GitHub Actions (lint, typecheck, tests, Gitleaks, Semgrep, axe-core)
- **Deploy:** Netlify (demo estática con mock data) + self-hosted (Docker)

## Estructura del monorepo

```text
vnbot-mvp/
├── apps/web/             # React + Vite PWA
├── services/api/         # FastAPI backend
├── packages/
│   ├── domain/           # Shared Python domain (pure, no framework)
│   ├── ui/               # Shared React component lib
│   └── pixelart/         # Procedural pixelart engine
├── skills/               # Catalog (38 planned, 6 for Phase 0.7)
├── docs/                 # 14 canonical docs + adrs/
├── infra/docker/         # docker-compose.yml (placeholder for 0.3)
├── assets/mascot/        # Original spritesheet PNGs (concept art refs)
├── tests/e2e/            # Playwright tests
└── .github/workflows/    # CI
```

## Inicio rápido

```bash
# Requisitos: Node 20+, pnpm 9+, Python 3.12+, uv

# 1. Instalar dependencias
make install

# 2. Copiar .env.example a .env y ajustar valores
cp .env.example .env

# 3. Ejecutar migraciones iniciales (cuando estén listas)
make migrate

# 4. Iniciar dev (frontend + backend en paralelo)
make dev
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000 (docs en /docs)

## Documentación

Los 14 documentos canónicos están en [`docs/`](./docs/):

- [Documento Maestro](./docs/00-DOCUMENTO-MAESTRO-VNBOT.md)
- [PRD](./docs/01-PRD-VNBOT.md)
- [TRD](./docs/02-TRD-VNBOT.md)
- [Esquema Backend](./docs/03-ESQUEMA-BACKEND-VNBOT.md)
- [Plan Implementación](./docs/04-PLAN-IMPLEMENTACION-VNBOT.md)
- [Diseño UI/UX](./docs/05-DISENO-UI-UX-VNBOT.md)
- ... y 8 más (App Flow, Modelo Datos, Seguridad, MCP, Roadmap, Sync, Testing, Gobernanza)

ADRs en [`docs/adrs/`](./docs/adrs/).

## Licencia

Código bajo MIT. Assets visuales, fuentes, modelos y dependencias pueden tener licencias diferentes — ver [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md) (pendiente).
