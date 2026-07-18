# VNBOT — Gobernanza de Proyecto

> **Documento:** Modelo de gobernanza y toma de decisiones
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Definición de gobernanza
> **Fecha:** 2026-07-17
> **Documentos relacionados:** [Documento Maestro](./00-DOCUMENTO-MAESTRO-VNBOT.md), [PRD](./01-PRD-VNBOT.md), [Roadmap](./10-ROADMAP-VNBOT.md), [Seguridad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md)

---

# 1. Propósito

Este documento define cómo se toman decisiones en VNBOT, quién tiene autoridad sobre qué, cómo se resuelven desacuerdos y cómo se gestiona la comunidad de contribuidores. La gobernanza no es burocracia: es la base para que un proyecto open source crezca sin fragmentarse ni estancarse.

VNBOT es un proyecto open source bajo licencia MIT. Cualquier persona puede usarlo, modificarlo y distribuirlo. Pero el desarrollo del proyecto en sí necesita reglas claras para que las contribuciones sean predecibles, los cambios sean coherentes y la comunidad sepa qué esperar.

---

# 2. Principios de gobernanza

## 2.1. Mérito técnico, no jerarquía

Las decisiones técnicas se toman por la calidad del argumento y la evidencia, no por quién lo dice. Un contribuidor nuevo con un buen argumento pesa igual que un maintainer con un argumento débil.

## 2.2. Transparencia

Todas las decisiones significativas se documentan en ADRs (Architecture Decision Records). Las discusiones ocurren en issues o reuniones públicas. No hay decisiones de proyecto en canales privados.

## 2.3. Conservadurismo arquitectónico

VNBOT prefiere no cambiar algo a cambiarlo mal. Una nueva funcionalidad, dependencia o integración debe justificar su costo de mantenimiento a largo plazo. El roadmap y los principios canónicos son la defensa contra el scope creep.

## 2.4. Privacidad por defecto en la gobernanza

Las discusiones sobre datos de usuarios, seguridad o vulnerabilidades se manejan con la misma seriedad que el código. Los reportes de seguridad siguen el proceso definido en SECURITY.md.

## 2.5. La comunidad no es un foco group

VNBOT escucha a la comunidad, pero no implementa cada petición. Las funcionalidades se priorizan según los principios del PRD y el roadmap, no por el número de votos en un issue.

---

# 3. Roles

## 3.1. Maintainer (mantenedor)

Un maintainer tiene:

- Permiso de merge en la rama `main` y ramas de release.
- Responsabilidad de revisar PRs.
- Responsabilidad de mantener la coherencia arquitectónica.
- Capacidad de emitir ADRs.
- Capacidad de aprobar releases.

**Requisitos para ser maintainer:**

- Mínimo 5 PRs significativos mergeados.
- Comprensión demostrada de los principios canónicos y la arquitectura.
- Compromiso de revisión activa (mínimo 2 revisiones por mes).
- Aprobación de al menos 2 maintainers existentes.

**Revocación:**

- Inactividad > 3 meses sin aviso → acceso de merge suspendido.
- Violación del código de conducta → acceso revocado inmediatamente.

## 3.2. Contributor (contribuidor)

Cualquier persona que envíe un PR. Los contribuidores no necesitan permisos especiales para proponer cambios.

## 3.3. Triage team (equipo de triaje)

Contribuidores con permiso para:

- Etiquetar issues.
- Asignar prioridad.
- Cerrar issues duplicados o resueltos.
- Mover issues entre columnas del project board.

No tienen permiso de merge.

## 3.4. Security liaisons (enlaces de seguridad)

Maintainers con responsabilidad adicional:

- Recibir y procesar reportes de seguridad.
- Coordinar parches de seguridad.
- Publicar advisorys.
- Gestionar el programa de responsible disclosure.

---

# 4. Toma de decisiones

## 4.1. Decisiones rutinarias

Cosas como: corregir un bug, mejorar un test, actualizar una dependencia menor, añadir documentación.

- **Proceso:** PR normal + 1 approval (maintainer o contribuidor con experiencia).
- **Timeline:** Se mergea cuando esté listo, sin demora.

## 4.2. Decisiones técnicas significativas

Cosas como: añadir una nueva dependencia, cambiar un API endpoint, modificar el modelo de datos, añadir un nuevo tipo de agente.

- **Proceso:** PR + 2 approvals (al menos 1 maintainer) + ADR si afecta la arquitectura.
- **Timeline:** Período de comentarios de 7 días mínimo.
- **ADR:** Se crea un ADR con contexto, decisión, consecuencias y alternativas consideradas.

## 4.3. Decisiones estratégicas

Cosas como: cambiar la licencia, redefinir el alcance del producto, aceptar una integración con implicaciones éticas, cambiar el modelo de gobernanza.

- **Proceso:** RFC (Request for Comments) público + período de comentarios de 14 días + votación de maintainers.
- **Quórum:** Mayoría simple de maintainers activos.
- **Veto:** Cualquier maintainer puede vetar con una razón técnica documentada. El veto se resuelve con discusión y, si es necesario, una nueva votación después de 7 días.

## 4.4. Emergencias de seguridad

- Un security liaison puede mergear un parche sin el proceso normal si afecta una vulnerabilidad activa.
- El parche se publica dentro de las 48 horas.
- Se sigue con un ADR post-mortem público (sin exponer detalles que faciliten la explotación).

---

# 5. Architecture Decision Records (ADRs)

## 5.1. Formato

Cada ADR sigue la plantilla:

```markdown
# ADR-XXX: [Título]

## Estado

[Propuesta | Aceptada | Deprecada | Superseded por ADR-YYY]

## Contexto

¿Por qué se necesita esta decisión? ¿Qué problema resuelve?

## Decisión

¿Qué se decidió? ¿En qué consiste?

## Consecuencias

- Positivas: ...
- Negativas: ...
- Riesgos: ...

## Alternativas consideradas

1. ...
2. ...

## Referencias

- PR #...
- Issue #...
- Doc relacionado: ...
```

## 5.2. Archivo

Los ADRs viven en `docs/adrs/` con numeración secuencial: `0001-nombre-decision.md`, `0002-otra-decision.md`, etc.

## 5.3. ADRs iniciales sugeridos

- ADR-0001: Usar OpenTelemetry como estándar de observabilidad.
- ADR-0002: No usar localStorage como base de datos.
- ADR-0003: No llamar zero-knowledge a un flujo que envía plaintext a un LLM.
- ADR-0004: MCP no es autorización, es protocolo.
- ADR-0005: Version vectors para sincronización (no last-write-wins).
- ADR-0006: Pixel art cyberpunk como lenguaje visual (no glassmorphism).
- ADR-0007: Fallback heurístico obligatorio antes de depender de LLM.

---

# 6. Proceso de contribución

## 6.1. Antes de contribuir

1. Leer CONTRIBUTING.md (pendiente de crear).
2. Leer el código de conducta (CODE_OF_CONDUCT.md, pendiente de crear).
3. Revisar los issues abiertos y el roadmap para entender la dirección del proyecto.
4. Si es una contribución significativa, abrir un issue proponiendo el cambio antes de escribir código.

## 6.2. Tipos de contribución y requisitos

| Tipo | Requisitos | Proceso |
|---|---|---|
| Corrección de docs | Ninguno especial | PR + 1 approval |
| Bug fix | Test que reproduce el bug + fix | PR + 1 approval |
| Nueva funcionalidad | Issue aprobado + tests + docs | PR + 2 approvals + posible ADR |
| Nueva integración MCP | Issue aprobado + contract tests + security review | PR + 2 approvals (1 maintainer) + security review |
| Nuevo proveedor LLM | Tests unitarios + mock | PR + 1 approval |
| Nuevo componente UI | Accesibilidad verificada + tests | PR + 1 approval |
| Cambio en modelo de datos | ADR + migración reversible | PR + 2 approvals + ADR |
| Cambio en seguridad | Security review obligatorio | PR + 2 approvals + security review |

## 6.3. CLA (Contributor License Agreement)

VNBOT usa licencia MIT, por lo que los contribuidores mantienen el copyright de su código y lo licencian bajo MIT. No se requiere un CLA separado, pero:

- Cada contribuidor debe confirmar que el código es original o que tiene derecho a contribuirlo bajo MIT.
- Si el código incluye trabajos de terceros, deben estar documentados en THIRD_PARTY_NOTICES.md.
- Los assets visuales (sprites, iconos, ilustraciones) pueden tener licencias diferentes y deben documentarse en el inventario de assets.

---

# 7. Gestión de la comunidad

## 7.1. Canales

| Canal | Propósito | Moderación |
|---|---|---|
| GitHub Issues | Bugs, features, preguntas | Triage team |
| GitHub Discussions | Ideas, preguntas generales, mostrando trabajo | Community |
| Discord/Matrix (futuro) | Chat en tiempo real | Moderators |

## 7.2. Código de conducta

VNBOT adoptará el Contributor Covenant v2.1 (o similar) como código de conducta. Las violaciones se manejan de acuerdo con el proceso definido en CODE_OF_CONDUCT.md.

## 7.3. Reconocimiento

- Todos los contribuidores se reconocen en el changelog.
- Los contribuidores significativos se mencionan en README.md.
- No hay sistema de "nivel" ni jerarquía de contribuidores más allá de los roles definidos.

---

# 8. Gestión de releases

## 8.1. Release manager

Cada release tiene un release manager asignado (un maintainer). Es responsable de:

- Verificar que todos los criterios de salida de la fase se cumplen.
- Coordinar el freeze de features.
- Ejecutar el release checklist.
- Publicar las release notes.
- Coordinar el rollout y monitorear errores post-release.

## 8.2. Ciclo de release

```text
Feature freeze → Code freeze → QA → Release candidate → Release → Post-release monitoring
```

## 8.3. Rollback

Si un release tiene un bug crítico:

1. El release manager decide si hacer rollback o hotfix.
2. Si rollback: se revierte a la versión anterior y se publica un advisory.
3. Si hotfix: se prepara un parche en la rama de release y se publica una versión parche.
4. Se documenta el incidente en un ADR post-mortem.

---

# 9. Evolución de la gobernanza

## 9.1. Revisión

Este documento se revisa cada 6 meses o cuando el equipo de maintainers cambie significativamente.

## 9.2. Cambios en la gobernanza

Los cambios a este documento siguen el proceso de "Decisiones estratégicas" (sección 4.3): RFC + 14 días de comentarios + votación de maintainers.

## 9.3. Cuando el proyecto crezca

Si VNBOT llega a tener más de 5 maintainers activos o más de 100 contribuidores, se debe considerar:

- Crear subequipos (core, UI, integraciones, seguridad).
- Definir un proceso de elección de maintainers más formal.
- Establecer un presupuesto (si hay financiación).
- Crear un consejo asesor (technical advisory board).

Estas decisiones se tomarán cuando sea necesario, no antes.

---

# 10. Documentos relacionados

- [Documento Maestro](./00-DOCUMENTO-MAESTRO-VNBOT.md) — Principios canónicos.
- [PRD](./01-PRD-VNBOT.md) — Objetivos de producto.
- [Roadmap](./10-ROADMAP-VNBOT.md) — Fases y prioridades.
- [Seguridad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md) — Proceso de seguridad.
- [Plan de Implementación](./04-PLAN-IMPLEMENTACION-VNBOT.md) — Tareas y dependencias.