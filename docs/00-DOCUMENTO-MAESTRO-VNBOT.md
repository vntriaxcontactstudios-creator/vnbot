# VNBOT — Documento Maestro

## 1. Resumen

VNBOT es un asistente personal open source, privado, autoalojable y extensible. Convierte texto, voz, imágenes y enlaces en memoria, recordatorios, listas, eventos y acciones controladas. Su memoria personal utiliza un grafo limitado de nodos y relaciones visible para el usuario. MCP permite añadir herramientas externas y conectar grafos especializados como Graphify sin hacerlos obligatorios.

VNBOT se distribuirá como:

- Demo estática en GitHub Pages.
- PWA/web.
- APK Android.
- Aplicación desktop mediante Tauri.
- Docker para servidores.
- CLI para instalaciones locales.

## 2. Principios canónicos

- Local-first cuando sea posible.
- El usuario controla sus datos, modelos, agentes y permisos.
- El LLM propone; el dominio valida; el ejecutor actúa.
- MCP es extensibilidad, no autorización.
- Recordatorios deterministas y auditables.
- Memoria editable, con procedencia y confianza.
- No usar APIs no oficiales.
- Pixel art cyberpunk original, sin copiar marcas ni assets.
- MIT para el código, con inventario separado de assets y dependencias.
- Testing y observabilidad desde el día uno. Cada módulo debe tener cobertura mínima definida, tests de integración para flujos críticos y tracing con OpenTelemetry.
- Sincronización diseñada antes de multiplataforma. La estrategia de sync entre dispositivos debe estar documentada y probada antes de distribuir APK, desktop y CLI.

## 3. Arquitectura canónica

```text
Web/PWA · APK · Desktop · CLI
              ↓
API versionada
              ↓
Domain services ─ Memory/Graph ─ Reminders
              ↓
Queue + Workers + Scheduler
              ↓
LLM Router ─ Skills ─ Policy Engine
              ↓
MCP Gateway e integraciones oficiales
```

### Persistencia

- PWA: IndexedDB.
- Local/desktop: SQLite.
- Servidor: PostgreSQL + pgvector.
- Archivos: almacenamiento S3-compatible/MinIO.
- Cache y colas: Redis.

## 4. MVP canónico

1. Cuenta o modo local.
2. Chat de texto.
3. Recordatorios puntuales y recurrentes.
4. Memoria explícita con nodos y relaciones.
5. Búsqueda textual y semántica local.
6. Grafo visible limitado.
7. Notificaciones web/locales.
8. Fallback heurístico sin LLM.
9. Exportación e importación cifrada.
10. Panel de auditoría.
11. Docker local.
12. Demo en GitHub Pages.

### 4.1. Compresión del MVP inicial

Para reducir el tiempo hasta un producto utilizable, las fases 0.1 (demo), 0.2 (núcleo local) y 0.3 (servidor) se pueden abordar como un único bloque de trabajo que entregue:

1. Web/PWA funcional con SQLite vía backend embebido o Docker local.
2. Chat con al menos un proveedor LLM + fallback heurístico documentado.
3. Memorias CRUD con búsqueda textual.
4. Recordatorios puntuales y recurrentes con scheduler durable.
5. Grafo básico de nodos y relaciones.
6. Exportación e importación cifrada.
7. Panel de auditoría.

La demo estática en GitHub Pages puede desarrollarse en paralelo como material de comunicación, sin bloquear el código funcional.

Esta estrategia permite entregar algo usable en semanas, no en meses, manteniendo la calidad y los principios del proyecto.

Audio, APK, desktop y MCP externo se incorporan después del núcleo fiable, aunque sus contratos se diseñan desde el principio.

## 5. Identidad visual

Mascota principal: golem informático original. La familia de agentes usa variantes del golem con diferentes accesorios, paletas y estados. Estados: idle, listening, thinking, processing, waiting_confirmation, success, warning, error, offline y sleeping.

La UI combina paneles HUD angulares, sprites pixel art, tipografía legible y animaciones discretas. No se utilizará glassmorphism ni blur como lenguaje principal.

## 6. Decisiones críticas

- No usar localStorage como base de datos.
- No usar `node-cron` dentro de cada réplica.
- No usar rate limiting solo en memoria en producción.
- No llamar zero-knowledge a un flujo que envía plaintext a un LLM cloud.
- No permitir a un agente enviar mensajes o borrar datos sin política de confirmación.
- No hacer Graphify obligatorio para memoria personal.

## 7. Documentos relacionados

Consultar [PRD](./01-PRD-VNBOT.md), [TRD](./02-TRD-VNBOT.md), [Backend](./03-ESQUEMA-BACKEND-VNBOT.md), [UI/UX](./05-DISENO-UI-UX-VNBOT.md) y [App Flow](./06-APP-FLOW-VNBOT.md).
- [Estrategia de Sync](./11-ESTRATEGIA-SYNC-VNBOT.md)
- [Testing y Observabilidad](./12-TESTING-Y-OBSERVABILIDAD-VNBOT.md)
- [Gobernanza de Proyecto](./13-GOBERNANZA-DE-PROYECTO-VNBOT.md)
