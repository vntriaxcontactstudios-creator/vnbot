# VNBOT — Referencias visuales y análisis

## Contenido

Este paquete incluye las imágenes visuales adjuntas durante la definición del proyecto, una copia del prototipo técnico `MINBOT-TASK-DOC.md`, el documento UI/UX y dos assets generados como prototipos originales de VNBOT.

## 1. Golem pixel art — `01-golem-pixelart-reference.jpg`

### Observaciones

- Silueta de personaje robusta y fácilmente identificable.
- Armadura segmentada con lectura clara a baja resolución.
- Visor central como foco emocional.
- Paleta gris/violeta con acentos cyan.
- Volumen comunicado mediante clusters de píxeles, no mediante blur.
- Buena referencia para el cuerpo base del golem informático.

### Aplicación en VNBOT

- Mascota principal.
- Golem guardián para onboarding y pantalla Hoy.
- Base de proporciones para variantes por agente.
- Escalas objetivo: 16, 32, 64 y 128 px.

### No replicar

No copiar exactamente el personaje, su silueta, colores, pose, sprites ni detalles identificables. Se utiliza como referencia general de pixel art y lectura de personaje.

## 2. HUD — `02-ui-hud-reference.jpeg`

### Observaciones

- Interfaz organizada como módulos de consola.
- Paneles compactos con bordes técnicos.
- Indicadores, barras, tabs, controles y mini-widgets.
- Alta densidad informativa.
- Composición basada en un fondo oscuro y acentos amarillos/magenta.

### Aplicación en VNBOT

- Panel de control.
- Vista de agentes.
- Actividad y healthchecks.
- Configuración avanzada.
- Inventario de skills e integraciones.

### Mejora para VNBOT

VNBOT debe reducir la densidad en las vistas de uso diario. Los paneles técnicos se reservarán para Actividad, Integraciones, Diagnóstico y modo avanzado.

## 3. Hacking HUD — `03-hacking-hud-reference.jpg`

### Observaciones

- Foco central con conexiones radiales.
- Nodos periféricos diferenciados por color.
- Sensación de seguridad, acceso y sistema en proceso.
- Composición dinámica para comunicar una operación.

### Aplicación en VNBOT

- Pantalla de conexiones MCP.
- Estado del policy engine.
- Flujo de aprobación de herramientas.
- Vista de permisos de agente.
- Visualización de una operación en ejecución.

### Mejora para VNBOT

No usar el patrón radial en toda la aplicación. Reservarlo para permisos, conexiones y operaciones concretas para que conserve significado.

## 4. Frames futuristas — `04-futuristic-frames-reference.jpg`

### Observaciones

- Marcos rectangulares con esquinas recortadas.
- Líneas cyan de alto contraste.
- Componentes reutilizables.
- Separación clara entre contenedor y contenido.

### Aplicación en VNBOT

- `PixelPanel`.
- `HudFrame`.
- `ActionCard`.
- `MemoryCard`.
- `AgentCard`.
- Cards de integración.

### Restricción legal

La imagen incluye marca de agua de stock. No debe utilizarse como asset final ni incluirse en la interfaz. Solo se conserva dentro de este paquete como referencia de análisis.

## 5. Elementos HUD cyan — `05-cyberpunk-hud-elements-reference.jpg`

### Observaciones

- Barras de progreso.
- Anillos y radares.
- Divisores.
- Etiquetas de estado.
- Marcos pequeños para datos.
- Lenguaje visual consistente basado en cyan y azul noche.

### Aplicación en VNBOT

- Loading states.
- Barras de progreso de jobs.
- Healthchecks.
- Indicadores de sincronización.
- Estado de audio/transcripción.
- Componentes de diagnóstico.

### Restricción legal

La imagen incluye marca de agua de stock. No debe reutilizarse como recurso de producción.

## 6. Síntesis visual de VNBOT

La raíz visual aprobada para VNBOT es:

```text
Golem informático original
+ pixel art limpio
+ HUD cyberpunk modular
+ paleta dark navy/cyan/magenta/amber
+ paneles angulares
+ estados de operación visibles
+ tipografía legible
+ accesibilidad
+ sin blur como estructura
```

> **Nota (2026-07-17):** El inventario de assets de producción se ha ampliado con tres spritesheets adicionales (agentes, estados y emotes). Ver [Sección 11 — Inventario consolidado](#11-inventario-consolidado-de-sprites) para el detalle completo, y `VNBOT_SPRITESHEET_REFERENCE.md` para la referencia técnica del sistema procedural.

## 7. Mascota generada de VNBOT

### `assets-generated/vnbot-golem-mascot-variants.png`

Hoja conceptual con seis variantes:

1. Golem guardián — principal.
2. Golem amistoso — chat y captura.
3. Golem analista — búsqueda y grafo.
4. Golem trabajador con drones — workers y jobs.
5. Golem centinela — bóveda y permisos.
6. Golem archivista — memoria e historial.

Es un prototipo generado para dirección artística. Antes de producción requiere limpieza manual, revisión de paleta, separación por sprites, documentación de licencia y exportación en escalas enteras.

### `assets-generated/vnbot-golem-animation-sheet.png`

Hoja conceptual de estados:

- Idle.
- Listening.
- Thinking.
- Processing.
- Success.
- Warning.
- Error.
- Sleeping.

La implementación final debe conectar estos estados con la máquina de estados real del backend y respetar `prefers-reduced-motion`.

## 8. Agent spritesheet — `vnbot-golem-agent-spritesheet.png`

### Observaciones

- Siete variantes del golem diferenciadas por rol, paleta y accesorio.
- Cada agente tiene una silueta reconocible a 64×64 px.
- Los accesorios son los principales diferenciadores: antenas, escudos, lentes, drones.
- Las paletas son coherentes con el sistema de color definido en el diseño UI/UX.
- La calidad de los píxeles es suficiente para referencia de dirección, pero requiere limpieza manual para producción.

### Aplicación en VNBOT

- Definición visual de los 7 agentes iniciales (Core, Chat, Archivist, Beacon, Navigator, Forge, Sentinel).
- Selector de agentes en la UI.
- Asignación por pantalla (ver tabla de correspondencia en UI/UX §19.2).
- Referencia para el sistema de rendering procedural (capas, paletas, accesorios).

### No replicar

No usar estos sprites directamente como assets de producción. Redibujar y limpiar píxeles según las especificaciones de UI/UX §28.

## 9. State spritesheet — `vnbot-golem-state-spritesheet.png`

### Observaciones

- Diez estados del golem principal en un solo sheet.
- Los estados cubren todo el ciclo de operación: idle → listening → thinking → processing → waiting_confirmation → success → warning → error → offline → sleeping.
- El estado `offline` muestra claramente el visor apagado, sin confundirse con `sleeping`.
- El estado `error` evita flashes excesivos (importante para accesibilidad y fotosensibilidad).
- La transición entre estados se logra intercambiando frames, no interpolando.

### Aplicación en VNBOT

- Definición visual de los 10 estados operativos de la mascota.
- Mapeo directo a los estados globales de la aplicación (ver App Flow §4.10).
- Referencia para la máquina de estados del componente `<MascotStateView>`.
- Base para los tests visuales de cada estado.

### Regla de producción

Cada estado debe exportarse como frame individual o como strip de sprites indexada. No se incrusta texto dentro del sprite — las etiquetas de estado se implementan como texto accesible fuera de la imagen.

## 10. UI emotes sheet — `vnbot-golem-ui-emotes.png`

### Observaciones

- Doce emotes compactos para contextos donde el sprite completo no cabe.
- Resolución target: 16×16 o 32×32 px.
- Los emotes son estáticos (no requieren animación).
- Cubren los mismos estados que el state spritesheet más variantes de emoción (happy, curious, focused, sleepy).

### Aplicación en VNBOT

- Burbujas de chat: emote del agente junto a su mensaje.
- Toasts: emote junto a notificación breve.
- Badges: icono de estado en cards de agente.
- Notificaciones push: centro de la notificación.
- Lista de agentes: emote pequeño indicando estado actual.
- Mensajes de estado del sistema: emote junto a texto de error/éxito.

### Regla de producción

Los emotes se exportan como sprites individuales de 16×16 y 32×32 px. Se implementan como `<img>` con `alt` descriptivo o como CSS background-image con `aria-label`.

## 11. Inventario consolidado de sprites

| Archivo | Frames/Variantes | Resolución base | Uso principal |
|---|---|---|---|
| `vnbot-golem-mascot-variants.png` | 6 variantes | 128×128 | Dirección artística, onboarding |
| `vnbot-golem-animation-sheet.png` | 9 estados (original) | 64×64 | Referencia de animación original |
| `vnbot-golem-agent-spritesheet.png` | 7 agentes | 64×64 | Variante por agente, selector |
| `vnbot-golem-state-spritesheet.png` | 10 estados | 64×64 | Estados operativos de mascota |
| `vnbot-golem-ui-emotes.png` | 12 emotes | 16×16 / 32×32 | Chat, toasts, badges, notificaciones |

Todos son concept art. Antes de producción: limpieza, separación de frames, metadata de licencia, pruebas sobre fondos claros y oscuros, exportación PNG indexado.

## 12. UI/UX Pro Max como referencia lógica

Se consultó `nextlevelbuilder/ui-ux-pro-max-skill`:

https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

Se incorporan sus patrones de proceso:

- Priorizar accesibilidad.
- Validar touch targets.
- Usar responsive mobile-first.
- Revisar estados de loading/error/empty.
- Usar tokens semánticos.
- Controlar performance y CLS.
- Motion de 150–300 ms con significado.
- No depender del hover.
- Validar formularios.
- Ofrecer navegación predecible.

No se copia el estilo visual del repositorio. El lenguaje de VNBOT continúa siendo pixel art cyberpunk.

## 13. Reglas de producción

- No usar imágenes con watermarks.
- No copiar personajes o interfaces reconocibles.
- Mantener inventario de assets.
- Registrar origen, modelo, prompt, fecha y licencia.
- Limpiar manualmente el pixel art generado.
- Usar nearest-neighbor para escalado.
- Probar alto contraste y reduced motion.
- Separar decoración de información operativa.
