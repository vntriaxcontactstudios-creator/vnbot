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

**Fase 0.1 — MVP comprimido** (en desarrollo). Documentación completa en [`docs/`](./docs/). Implementación siguiendo el [Plan de Implementación](./docs/04-PLAN-IMPLEMENTACION-VNBOT.md).

## Stack tecnológico (Fase 0.1)

- **Frontend:** React 19 + Vite + TypeScript strict + Tailwind 4 + TanStack Query + Zustand + Dexie + Atropos.js + anime.js
- **Backend:** Python 3.12 + FastAPI + Pydantic v2 + SQLAlchemy 2 async + Alembic + Uvicorn
- **DB:** SQLite (WAL mode) — PostgreSQL en 0.3
- **LLM:** Z.AI (glm-4.6, sin API key requerida) — Ollama como fallback
- **Observabilidad:** OpenTelemetry SDK desde día 1
- **Testing:** Vitest + pytest + Playwright + axe-core
- **CI:** GitHub Actions (lint, typecheck, tests, Gitleaks, Semgrep, axe-core)

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
