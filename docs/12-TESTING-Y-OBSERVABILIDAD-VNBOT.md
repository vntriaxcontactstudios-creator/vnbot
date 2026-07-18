# VNBOT — Testing y Observabilidad

> **Documento:** Estrategia de testing y observabilidad
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Requisitos de calidad y monitoreo
> **Fecha:** 2026-07-17
> **Documentos relacionados:** [TRD](./02-TRD-VNBOT.md), [Backend](./03-ESQUEMA-BACKEND-VNBOT.md), [Roadmap](./10-ROADMAP-VNBOT.md)

---

# 1. Propósito

Este documento define la estrategia de testing y observabilidad de VNBOT. Testing y observabilidad no son fases posteriores al desarrollo; son requisitos que se implementan desde la primera línea de código.

VNBOT procesará datos personales, recordatorios temporales y operaciones con consecuencias reales (enviar un correo, modificar un calendario). Un bug silencioso puede hacer que un recordatorio no se dispare o que una memoria se pierda. La estrategia de testing y observabilidad existe para prevenir eso.

---

# 2. Principios

## 2.1. Tests por defecto

Cada módulo nuevo debe incluir tests. No se aceptan PRs sin tests para el código afectado.

## 2.2. Pirámide de tests

```text
        /  E2E  \           → Flujos críticos (pocos, lentos, caros)
       / Contract \         → MCP tools, API boundaries
      / Integration \       → Servicios + storage + colas
     /    Unit      \       → Lógica de dominio, parsers, utils
    /________________\      → Muchos, rápidos, baratos
```

## 2.3. Observabilidad sin contenido privado

Los traces, logs y métricas nunca contienen el contenido de memorias, mensajes ni datos personales del usuario. Solo metadatos operativos: IDs, duraciones, estados, tipos, contadores.

## 2.4. Automatizado en CI

Todo lo que se pueda automatizar, se automatiza. Las auditorías manuales se reservan para releases.

---

# 3. Testing por capa

## 3.1. Unit tests

### Cobertura mínima por módulo

| Módulo | Cobertura mínima | Prioridad |
|---|---|---|
| Dominio (memory, reminder, graph, list) | 80% | P0 |
| LLM Router (selección, fallback, parsing) | 75% | P0 |
| Policy Engine | 90% | P0 |
| Heurística de parseo | 85% | P0 |
| API validators (Zod schemas) | 80% | P0 |
| MCP Gateway (routing, scopes) | 70% | P1 |
| Sync engine | 75% | P1 |
| Frontend utils | 70% | P1 |
| Frontend components | 60% | P1 |

### Herramientas

- **Backend (Python):** pytest + pytest-asyncio + pytest-cov.
- **Frontend (TypeScript):** Vitest + @testing-library/react.

### Reglas

- Cada test tiene un nombre descriptivo que explica el escenario.
- Los tests de dominio no tocan la red, el filesystem ni la base de datos.
- Los mocks se usan solo en las fronteras (LLM, MCP, storage).

## 3.2. Integration tests

### Escenarios obligatorios

```text
1. Chat → interpretar intención → crear memoria → verificar en storage.
2. Chat → crear recordatorio → scheduler lo dispara → notificación emitida.
3. Crear recordatorio recurrente → generar instancias → completar una → verificar siguiente.
4. Crear nodo A → crear edge A→B → buscar subgrafo desde A → verificar resultado.
5. Conectar MCP tool → llamar tool → verificar resultado → verificar auditoría.
6. Exportar datos → importar en workspace limpio → verificar integridad.
7. Crear conflicto de sync → resolver → verificar estado final.
8. Fallback heurístico → parsear "recuérdame X mañana a las 5" → crear recordatorio correcto.
```

### Herramientas

- **Backend:** pytest + testcontainers (PostgreSQL, Redis) para tests de integración reales.
- **Frontend:** Vitest + MSW (Mock Service Worker) para API mocking.

## 3.3. E2E tests

### Flujos críticos

```text
1. Onboarding → crear primera memoria → buscarla → verla en el grafo.
2. Crear recordatorio → esperar disparo → ver notificación → completarlo.
3. Configurar LLM → chatear → crear memoria por conversación → editarla.
4. Crear agente → asignar skills → usar agente → verificar permisos.
5. Exportar → limpiar → importar → verificar que todo está ahí.
```

### Herramientas

- **Playwright** para web/PWA.
- **Appium** o **Maestro** para APK (fase 0.3+).
- **Tauri driver** para desktop (fase 0.3+).

### Reglas

- Los E2E tests se ejecutan en CI para cada PR en la rama principal.
- Se usan fixtures con datos de prueba, nunca datos reales.
- Los E2E tests no dependen de un LLM real (se usa un mock).

## 3.4. Contract tests

### MCP tools

Cada tool MCP debe tener contract tests que verifiquen:

- Input schema válido.
- Output schema válido.
- La tool respeta sus scopes declarados.
- Fallo aislado (no propaga al sistema).
- Timeout respetado.

### API endpoints

Cada endpoint de la API `/api/v1` debe tener tests de contrato que verifiquen:

- Request schema válido.
- Response schema válido.
- Status codes correctos (200, 201, 400, 401, 403, 404, 409, 422, 500).
- Headers de respuesta correctos (Content-Type, Cache-Control, Rate-Limit).

### Herramientas

- **Pact** para contract testing entre servicios.
- **Zod** para validación de schemas en tests.

## 3.5. Security tests

Ver [Seguridad y Privacidad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md) para el plan completo.

Resumen de lo que se ejecuta en CI:

- Gitleaks (secretos en commits).
- Semgrep (SAST).
- npm audit / pip-audit (dependencias).
- Trivy (contenedores Docker).
- OWASP ZAP (DAST, antes de releases).

---

# 4. Benchmarks automatizados

## 4.1. Grafo

| Operación | Volumen | Latencia P95 objetivo |
|---|---|---|
| Crear nodo | 5,000 nodos existentes | < 50ms |
| Crear edge | 10,000 edges existentes | < 50ms |
| Búsqueda textual | 5,000 nodos | < 100ms |
| Búsqueda semántica | 5,000 nodos con embeddings | < 200ms |
| Subgrafo profundidad 2 | 20 nodos resultado | < 300ms |
| Subgrafo profundidad 3 | 50 nodos resultado | < 500ms |

## 4.2. Recordatorios

| Operación | Volumen | Criterio |
|---|---|---|
| Crear 1,000 recordatorios | Batch | < 10s total, 0 duplicados |
| Disparo de 100 recordatorios en mismo minuto | Concurrente | 0 duplicados, todos disparados |
| Scheduler tick con 1,000 jobs | 1 job/segundo | 0 perdidos, 0 duplicados |

## 4.3. Ejecución

Los benchmarks se ejecutan en CI como un job separado. Los resultados se comparan con el baseline anterior. Si P95 degrada más de 20% en una operación P0, el CI falla.

---

# 5. Observabilidad

## 5.1. Estándar: OpenTelemetry

VNBOT usa OpenTelemetry como estándar unificado de observabilidad. Esto permite cambiar backend de observabilidad (Jaeger, Tempo, Datadog, etc.) sin cambiar el código de instrumentación.

## 5.2. Spans obligatorios

| Span | Atributos |
|---|---|
| `vnbot.api.<method>.<endpoint>` | method, endpoint, status_code, workspace_id |
| `vnbot.domain.memory.<operation>` | operation, node_id, workspace_id |
| `vnbot.domain.reminder.<operation>` | operation, reminder_id, workspace_id |
| `vnbot.domain.graph.<operation>` | operation, depth, result_count |
| `vnbot.llm.<provider>.call` | provider, model, tokens_in, tokens_out, latency_ms |
| `vnbot.mcp.<tool_name>.call` | tool_name, status, latency_ms |
| `vnbot.worker.<job_type>.execute` | job_type, job_id, status, attempts |
| `vnbot.sync.push` | device_id, ops_count, conflicts_count |
| `vnbot.sync.pull` | device_id, ops_received |

## 5.3. Métricas obligatorias

### Contadores

- `vnbot_api_requests_total{method, endpoint, status_code}`
- `vnbot_llm_tokens_total{provider, model, direction}`
- `vnbot_jobs_total{type, status}`
- `vnbot_sync_conflicts_total{workspace_id}`
- `vnbot_mcp_tool_calls_total{tool_name, status}`

### Histogramas

- `vnbot_api_duration_seconds{method, endpoint}`
- `vnbot_llm_duration_seconds{provider, model}`
- `vnbot_jobs_duration_seconds{type}`
- `vnbot_graph_query_duration_seconds{operation}`
- `vnbot_sync_operation_duration_seconds{type}`

### Gauges

- `vnbot_active_reminders{workspace_id}`
- `vnbot_memory_nodes_total{workspace_id}`
- `vnbot_pending_sync_operations{device_id}`
- `vnbot_worker_queue_size{type}`

## 5.4. Logs estructurados

Todos los logs usan formato JSON con campos estándar:

```json
{
  "timestamp": "2026-07-17T10:00:00.000Z",
  "level": "info",
  "service": "vnbot-api",
  "trace_id": "abc123",
  "span_id": "def456",
  "message": "Memory created",
  "workspace_id": "uuid",
  "node_id": "uuid",
  "provenance": "explicit_user_input"
}
```

Niveles: `error`, `warn`, `info`, `debug`.

Nunca incluir contenido de memorias, mensajes de chat, ni datos personales en los logs.

## 5.5. Dashboards

### Por release

- Request rate y error rate de la API.
- Latencia P50/P95/P99 de endpoints principales.
- Jobs ejecutados vs fallidos.
- Sync: operaciones exitosas vs conflictos.
- LLM: tokens consumidos por provider y modelo.

### Por módulo

- Vista detallada de spans y métricas de cada módulo.
- Waterfall de traces para debuggear flujos completos.

### Alertas (fase 0.2+)

- Error rate > 5% en cualquier endpoint.
- P99 > 2s en endpoints principales.
- Jobs fallidos > 10 en la última hora.
- Sync conflicts > 50 sin resolver en 24 horas.
- Scheduler tick fallido.

## 5.6. Implementación por fase

| Fase | Observabilidad |
|---|---|
| 0.1 MVP | Spans en API y dominio. Logs estructurados. Métricas básicas en consola. |
| 0.2 Servidor | OpenTelemetry con collector. Dashboards básicos. Alertas iniciales. |
| 0.3+ | Tracing distribuido completo. Alertas por módulo. Dashboards por release. |

---

# 6. Cobertura y calidad en CI

## 6.1. Pipeline por PR

```text
1. Lint (ESLint / Ruff / Biome)
2. Typecheck (TypeScript / mypy)
3. Unit tests + coverage report
4. Integration tests
5. Secret scan (Gitleaks)
6. SAST (Semgrep)
7. Accessibility (axe-core para frontend)
8. Build verification
```

## 6.2. Pipeline por release

```text
1. Todo lo del PR pipeline
2. E2E tests completos
3. Benchmarks automatizados
4. DAST (OWASP ZAP)
5. Container scan (Trivy)
6. Dependency audit completo
7. Accessibility audit manual (keyboard + screen reader)
8. SBOM generation
```

## 6.3. Criterios de calidad

| Criterio | Umbral | Acción si falla |
|---|---|---|
| Cobertura unitaria (core) | < 60% | PR bloqueada |
| Cobertura unitaria (core) | < 80% | Warning, no bloquea |
| Tests fallidos | > 0 | PR bloqueada |
| Lint errors | > 0 | PR bloqueada |
| Secret scan | > 0 | PR bloqueada, alerta de seguridad |
| SAST findings (high) | > 0 | PR bloqueada |
| axe-core violations (critical) | > 0 | PR bloqueada |
| Benchmark degradation > 20% | En cualquier operación P0 | PR bloqueada |

---

# 7. Documentos relacionados

- [TRD](./02-TRD-VNBOT.md) — Arquitectura general y principios técnicos.
- [Backend](./03-ESQUEMA-BACKEND-VNBOT.md) — Instrumentación específica por servicio.
- [Roadmap](./10-ROADMAP-VNBOT.md) — Fases y criterios de salida.
- [Seguridad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md) — Tests de seguridad.
- [UI/UX](./05-DISENO-UI-UX-VNBOT.md) — Accesibilidad y performance budgets.