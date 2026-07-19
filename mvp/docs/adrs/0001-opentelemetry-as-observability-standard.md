# ADR-0001: Use OpenTelemetry as observability standard

## Estado

Aceptada

## Contexto

VNBOT necesita observabilidad desde el día 1 (TRD §24, Testing §5). Los requirements son:

- Tracing distribuido (cuando se separen los servicios en 0.3)
- Métricas (request rate, error rate, P95 latency, queue size)
- Logs estructurados (JSON con trace_id, span_id, workspace_id)
- Nunca loguear plaintext/audio/secrets/tokens/PII
- Permitir swap de backend (Jaeger, Tempo, Datadog) sin cambiar el código

Las alternativas consideradas fueron:

1. **OpenTelemetry** — estándar CNCF, vendor-neutral, soporte nativo en Python y JS
2. **Prometheus + Grafana Loki + Jaeger** — stack self-hosted popular
3. **Datadog / New Relic** — SaaS con costos
4. **Console.log + grep** — insuficiente para distributed tracing

## Decisión

Adoptar **OpenTelemetry** como único estándar de observabilidad. Específicamente:

- `opentelemetry-sdk` Python (backend) y `@opentelemetry/sdk-node` JS (frontend)
- Exporter OTLP (gRPC para producción, HTTP para dev)
- Spans obligatorios: `vnbot.api.*`, `vnbot.domain.*`, `vnbot.llm.*`, `vnbot.mcp.*`
- Counters: `vnbot_api_requests_total`, `vnbot_llm_tokens_total`, `vnbot_jobs_total`
- Histograms: `vnbot_api_duration_seconds`, `vnbot_graph_query_duration_seconds`
- Gauges: `vnbot_active_reminders`, `vnbot_worker_queue_size`
- Logs estructurados JSON con `trace_id` y `span_id` en cada entry
- Backend swap (Jaeger → Tempo → Datadog) sin cambiar código — solo exporter config

## Consecuencias

- **Positivas**: Vendor-neutral, estándar CNCF, soporte nativo en ambos lenguajes, spec estable, comunidad activa.
- **Negativas**: Overhead de runtime (~3-5% CPU), bundle size +14 KB gz en frontend.
- **Riesgos**: Complejidad inicial de setup, curva de aprendizaje para equipos nuevos en OTel.

## Alternativas consideradas

1. **Prometheus + Grafana Loki + Jaeger** — stack más fragmentado, requiere integración manual entre componentes. OpenTelemetry unifica todo.
2. **Datadog / New Relic** — costos mensuales, vendor lock-in. VNBOT es open source y debe ser self-hosteable.
3. **Console.log + grep** — insuficiente para distributed tracing cuando se separen los servicios en 0.3.

## Referencias

- TRD §24 #1 (frozen decision)
- Testing §5 (OTel setup, mandatory spans/metrics)
- Phase 0.1 feature F11 (OpenTelemetry tracing)
- Plan §4 (Phase 0 preparation deliverables)
