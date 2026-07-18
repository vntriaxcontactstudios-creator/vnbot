# VNBOT — Documentación del proyecto

Esta carpeta contiene la documentación de producto, arquitectura, backend, implementación, diseño, seguridad y extensibilidad de VNBOT.

## Fuente de entrada

Comienza por el [README principal](../README.md) y después revisa el [Documento Maestro](./00-DOCUMENTO-MAESTRO-VNBOT.md).

## Documentos

1. [Documento Maestro](./00-DOCUMENTO-MAESTRO-VNBOT.md) — visión ejecutiva y decisiones canónicas.
2. [PRD](./01-PRD-VNBOT.md) — objetivos, usuarios, alcance y requisitos de producto.
3. [TRD](./02-TRD-VNBOT.md) — arquitectura y requisitos técnicos.
4. [Esquema Backend](./03-ESQUEMA-BACKEND-VNBOT.md) — servicios, API, entidades operativas, jobs y workers.
5. [Plan de Implementación](./04-PLAN-IMPLEMENTACION-VNBOT.md) — fases, tareas, milestones y releases.
6. [Diseño UI/UX](./05-DISENO-UI-UX-VNBOT.md) — pixel art, HUD, mascotas, componentes y accesibilidad.
7. [App Flow](./06-APP-FLOW-VNBOT.md) — rutas, pantallas, estados y recorridos.
8. [Modelo de Datos](./07-MODELO-DATOS-VNBOT.md) — entidades, relaciones, persistencia y exportación.
9. [Seguridad y Privacidad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md) — amenazas, cifrado, permisos e incidentes.
10. [MCP y Skills](./09-MCP-Y-SKILLS-VNBOT.md) — tools, scopes, agentes y extensibilidad.
11. [Roadmap](./10-ROADMAP-VNBOT.md) — evolución desde demo hasta versión estable.
12. [Estrategia de Sync](./11-ESTRATEGIA-SYNC-VNBOT.md) — sincronización multi-dispositivo, version vectors y resolución de conflictos.
13. [Testing y Observabilidad](./12-TESTING-Y-OBSERVABILIDAD-VNBOT.md) — pirámide de tests, benchmarks, OpenTelemetry y calidad en CI.
14. [Gobernanza de Proyecto](./13-GOBERNANZA-DE-PROYECTO-VNBOT.md) — roles, toma de decisiones, ADRs y proceso de contribución.

## Orden recomendado de lectura

### Para producto

```text
00 → 01 → 05 → 06 → 10
```

### Para backend

```text
00 → 02 → 03 → 07 → 08 → 12 → 04
```

### Para IA, MCP y agentes

```text
01 → 02 → 07 → 08 → 09 → 10
```

### Para infraestructura y calidad

```text
00 → 12 → 11 → 08 → 02
```

### Para comunidad

```text
README principal → 00 → 13 → 04 → 10 → CONTRIBUTING
```

## Fuente de verdad

Cuando exista contradicción:

1. Código y contratos versionados.
2. Documento Maestro.
3. TRD y Esquema Backend.
4. PRD.
5. Planes y documentos auxiliares.

## Estado

- Producto: VNBOT.
- Licencia prevista: MIT.
- Fase: definición y preparación del MVP.
- Fecha: 2026-07-17 (actualización con docs 11, 12, 13).
