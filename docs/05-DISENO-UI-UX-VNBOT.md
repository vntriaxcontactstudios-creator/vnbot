# VNBOT — Diseño UI/UX

> **Documento:** Diseño de interfaz y experiencia de usuario
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Dirección visual y sistema de experiencia
> **Fecha:** 2026-07-16
> **Documentos relacionados:** [PRD](./01-PRD-VNBOT.md), [TRD](./02-TRD-VNBOT.md), [App Flow](./06-APP-FLOW-VNBOT.md)
> **Assets de referencia:** `vnbot-golem-mascot-variants.png`, `vnbot-golem-animation-sheet.png`

---

# 1. Propósito

Este documento define cómo debe verse, sentirse y comportarse VNBOT en web, PWA, APK y desktop. La interfaz debe comunicar que VNBOT es una memoria personal y un sistema de agentes, no solamente un chat con una mascota decorativa.

El diseño combinará:

- Pixel art de alta calidad.
- HUD cyberpunk modular.
- Paneles de consola.
- Mascotas con estados emocionales.
- Grafo de memoria.
- Información operativa clara.
- Animaciones cortas y significativas.
- Accesibilidad y legibilidad.

El estilo visual debe ser propio. Las imágenes proporcionadas por el usuario se utilizarán como referencias de composición, color y lenguaje, pero no se copiarán sus assets, marcas, textos, watermarks ni layouts de manera literal.

---

# 2. Principios de diseño

## 2.1. Claridad antes que decoración

El pixel art, los marcos HUD y la mascota deben reforzar la jerarquía, no ocultar la información. Si un usuario no entiende qué va a hacer el agente, la pantalla falla aunque sea visualmente atractiva.

## 2.2. La mascota refleja el estado real

La mascota no debe animarse de forma aleatoria mientras el backend está detenido. Cada estado visual debe corresponder a un estado real:

```text
idle                 → no hay operación activa
listening            → se está capturando audio o entrada
thinking             → se está clasificando la intención
processing           → existe un job en ejecución
waiting_confirmation → la acción espera al usuario
success              → operación completada
warning              → resultado parcial o configuración incompleta
error                → operación fallida
offline              → no hay conexión
sleeping             → modo de baja actividad
```

## 2.3. Densidad configurable

VNBOT debe funcionar para dos perfiles:

- Usuario casual: interfaz limpia, pocas métricas y acciones guiadas.
- Usuario avanzado: paneles, logs, permisos, jobs, agentes y métricas.

El modo avanzado no debe modificar las reglas de seguridad; solo expone más información.

## 2.4. Sin glassmorphism como estructura

No se utilizará blur gaussiano, transparencia excesiva ni “cristal” como lenguaje principal. Se usarán:

- Colores sólidos.
- Marcos pixelados.
- Sombras discretas de desplazamiento entero.
- Líneas de separación.
- Patrones de rejilla.
- Contraste de capas.
- Bordes angulares.

## 2.5. La acción debe ser reversible cuando sea posible

Las acciones destructivas, externas o ambiguas deben mostrar:

- Qué se hará.
- Con qué datos.
- Mediante qué herramienta.
- Con qué agente.
- Cómo cancelar o revocar.

---

# 3. Dirección artística

## 3.1. Concepto

VNBOT se presenta como un sistema operativo personal instalado en una estación cyberpunk. El usuario no “entra a una nube abstracta”; accede a una consola modular donde su memoria, tareas y agentes están organizados.

Metáforas visuales recomendadas:

- **Hoy:** centro de operaciones.
- **Memoria:** archivo/atlas de nodos.
- **Grafo:** red de conexiones.
- **Agentes:** hangar o roster de unidades.
- **Skills:** módulos instalables.
- **Integraciones:** conexiones externas.
- **Seguridad:** bóveda/centinela.
- **Jobs:** actividad del sistema.

Estas metáforas deben apoyar la navegación, no sustituir etiquetas textuales.

## 3.2. Referencias visuales analizadas

### Golem pixel art

Aporta:

- Silueta fuerte.
- Armadura segmentada.
- Visor como foco emocional.
- Lectura a baja resolución.
- Posibilidad de crear variantes por agente.

### HUD cyberpunk

Aporta:

- Paneles modulares.
- Barras de progreso.
- Indicadores de conexión.
- Retículas.
- Estados de seguridad.
- Jerarquía visual por color.

### Hacking HUD y paneles sci-fi

Aportan una sensación de sistema operativo técnico, pero deben simplificarse para no convertir la interfaz en una pantalla de videojuego ilegible.

### Sprite sheets

Aportan el patrón correcto para animar estados sin cargar cientos de imágenes individuales.

## 3.3. Referencias que no deben copiarse

- Watermarks.
- Logotipos.
- Nombres de videojuegos.
- Personajes reconocibles.
- Tipografías propietarias.
- Textos de UI de terceros.
- Paneles idénticos a una obra existente.

---

# 4. Sistema de color

## 4.1. Paleta base

```css
:root {
  --vnbot-void: #070A12;
  --vnbot-bg-0: #0A1020;
  --vnbot-bg-1: #101B2E;
  --vnbot-panel-0: #12243A;
  --vnbot-panel-1: #173653;
  --vnbot-panel-2: #1C4664;
  --vnbot-line: #2A6F8E;
  --vnbot-line-soft: #1D465E;
  --vnbot-text: #ECF6FF;
  --vnbot-text-muted: #91A9BE;
  --vnbot-cyan: #20DCE8;
  --vnbot-blue: #4D9DFF;
  --vnbot-magenta: #D94BE3;
  --vnbot-violet: #8A6CFF;
  --vnbot-amber: #FFC83D;
  --vnbot-green: #5BDF82;
  --vnbot-red: #FF5C6D;
  --vnbot-white: #FFFFFF;
}
```

## 4.2. Significado de colores

| Color | Significado |
|---|---|
| Cyan | Estado normal, memoria, sistema activo |
| Azul | Información, navegación, consulta |
| Magenta | Creatividad, agente especializado, acción experimental |
| Violeta | Grafo, relaciones, conocimiento |
| Amber | Atención, espera, procesamiento, próxima tarea |
| Verde | Completado, seguro, conexión correcta |
| Rojo | Error, bloqueo, riesgo o acción rechazada |

El color nunca debe ser el único indicador. Siempre debe existir texto, icono, patrón o estado accesible.

## 4.3. Temas

### Dark Core

Tema principal con fondos azul noche y líneas cyan.

### Amber Terminal

Tema de alto contraste con amber y verde sobre fondo oscuro.

### Violet Archive

Tema orientado a memoria y grafo.

### High Contrast

Reduce decoración y aumenta contraste.

### Custom

El usuario puede modificar colores de acento, pero no debe poder hacer ilegible el texto sin una advertencia de contraste.

---

# 5. Tipografía

## 5.1. Uso

- Títulos: fuente display pixel/tech.
- Navegación: fuente display o sans-serif compacta.
- Mensajes: sans-serif legible.
- Logs y JSON: monospace.
- Números de métricas: monospace o display tabular.

## 5.2. Reglas

- No utilizar una fuente pixelada para párrafos largos.
- Incluir fuentes localmente cuando la licencia lo permita.
- Tener fallback sans-serif.
- No depender de fuentes remotas en GitHub Pages offline.
- Respetar escala del sistema.
- Mínimo recomendado de 14–16 px para texto normal.

---

# 6. Grid, layout y responsive

## 6.1. Breakpoints

```text
xs  < 480px   → móvil compacto
sm  480–767px → móvil grande
md  768–1023px → tablet
lg  1024–1439px → desktop
xl  ≥ 1440px → desktop amplio
```

## 6.2. Desktop

Layout de tres zonas:

```text
Sidebar fija | Área principal | Inspector contextual
```

El inspector puede ocultarse para aumentar el espacio de chat, grafo o panel.

## 6.3. Tablet

- Sidebar colapsable.
- Inspector como drawer.
- Dos columnas solo en vistas de administración.

## 6.4. Móvil

- Navegación inferior o drawer.
- Una columna.
- Acciones primarias accesibles con el pulgar.
- Inspector como pantalla completa.
- Grafo con modo lista predeterminado si el dispositivo es pequeño.
- Mascota visible sin ocupar el área de escritura.

## 6.5. Área segura

En APK se deben respetar:

- Notch.
- Barra de navegación.
- Teclado virtual.
- Rotación.
- Modo pantalla pequeña.

---

# 7. Arquitectura de navegación

## 7.1. Navegación principal

```text
HOY
CHAT
MEMORIA
GRAFO
LISTAS
AGENTES
SKILLS
INTEGRACIONES
ACTIVIDAD
AJUSTES
```

## 7.2. Significado de cada sección

### Hoy

Vista operativa con lo que requiere atención ahora.

### Chat

Captura, consultas y acciones mediante lenguaje natural.

### Memoria

Búsqueda y administración de memorias en forma de lista.

### Grafo

Exploración visual de nodos y relaciones.

### Listas

Compras, tareas, colecciones e inventarios.

### Agentes

Configuración, estado, modelo, avatar y permisos de cada agente.

### Skills

Capacidades instaladas y disponibles.

### Integraciones

MCP, calendarios, correo, mensajería y otros conectores.

### Actividad

Jobs, operaciones, entregas, errores y auditoría.

### Ajustes

Cuenta, bóveda, privacidad, notificaciones, apariencia y datos.

---

# 8. Pantalla de bienvenida y onboarding

## 8.1. Objetivo

El onboarding debe explicar VNBOT sin abrumar con conceptos técnicos. El usuario debe comprender la diferencia entre:

- Capturar.
- Guardar memoria.
- Crear recordatorio.
- Conectar una herramienta.

## 8.2. Secuencia

```text
Bienvenida
  ↓
Elegir modo: Local / Servidor privado
  ↓
Configurar zona horaria
  ↓
Crear o desbloquear bóveda
  ↓
Elegir proveedor LLM o continuar sin LLM
  ↓
Seleccionar mascota base
  ↓
Crear primer recordatorio guiado
  ↓
Llegar a Hoy
```

## 8.3. Primera acción

El onboarding debe proponer una frase de ejemplo, pero permitir cambiarla. Después de crearla, se muestra:

- Interpretación.
- Fecha completa.
- Canal.
- Estado de almacenamiento.
- Mascota en estado success.

---

# 9. Panel “Hoy”

## 9.1. Objetivo

Responder en menos de cinco segundos a estas preguntas:

- ¿Qué debo hacer ahora?
- ¿Qué viene después?
- ¿Qué está atrasado?
- ¿Qué está procesando VNBOT?
- ¿Cómo capturo algo rápido?

## 9.2. Estructura

```text
┌────────────────────────────────────────────────────────────┐
│ VNBOT OS       16 JUL 2026       [Buscar] [Mascota] [Perfil]│
├───────────────┬──────────────────────────┬─────────────────┤
│ Navegación    │ Centro operativo         │ Estado agente   │
│               │                          │                 │
│ HOY           │ Próximo recordatorio     │ Golem activo    │
│ CHAT          │ Tareas atrasadas         │ thinking        │
│ MEMORIA       │ Agenda                   │                 │
│ GRAFO         │ Jobs                     │ [Cambiar]       │
│ LISTAS        │ Captura rápida            │                 │
│ AGENTES       │                          │                 │
└───────────────┴──────────────────────────┴─────────────────┘
```

## 9.3. Tarjeta de recordatorio

Debe mostrar:

- Título.
- Fecha y hora completas.
- Prioridad.
- Relación o proyecto.
- Canal.
- Acciones: completar, posponer, editar.

## 9.4. Tarjeta de job

Debe mostrar:

- Tipo de operación.
- Mascota/agent.
- Progreso si existe.
- Tiempo transcurrido.
- Cancelar si es cancelable.
- Ver detalles.

---

# 10. Chat

## 10.1. Objetivo

El chat es la entrada principal, pero no debe ocultar la estructura que VNBOT crea.

## 10.2. Estructura de mensaje del agente

```text
[AVATAR + AGENTE]
Respuesta humana breve.

[EVIDENCIA]
Memorias o fuentes utilizadas.

[ACCIÓN PROPUESTA]
Qué cambiará y cuándo.

[ESTADO]
Esperando confirmación / En cola / Completado.

[CONTROLES]
Editar · Confirmar · Cancelar · Ver log
```

## 10.3. Composer

Debe permitir:

- Texto.
- Micrófono.
- Adjuntar archivo.
- Seleccionar agente.
- Modo captura/consulta.
- Acceso a comandos rápidos.

## 10.4. Estados del chat

```text
empty
writing
recording
transcribing
thinking
processing
waiting_confirmation
success
partial_success
error
offline
```

## 10.5. Ambigüedad

Una tarjeta de aclaración debe ser más clara que un mensaje genérico:

```text
No puedo saber a qué hora quieres el recordatorio.

Fecha interpretada: viernes 17 de julio de 2026
Hora: pendiente

[08:00] [12:00] [18:00] [Elegir otra]
```

---

# 11. Memoria

## 11.1. Vista de lista

Cada memoria debe mostrar:

- Tipo.
- Título o resumen.
- Tags.
- Confianza.
- Fuente.
- Última actualización.
- Sensibilidad.
- Relaciones.

## 11.2. Vista de detalle

Panel con:

- Contenido.
- Metadata.
- Procedencia.
- Historial de cambios.
- Relaciones.
- Acciones: editar, corregir, olvidar, convertir en tarea.

## 11.3. Confianza

La confianza se muestra como texto:

```text
Confirmada por ti
Extraída de conversación
Inferida por el agente
En conflicto
```

No se debe mostrar solo un porcentaje sin explicación.

## 11.4. Olvidar

El botón “Olvidar” debe explicar:

- Qué nodo se eliminará.
- Qué relaciones dependen de él.
- Si existe un periodo de recuperación.
- Qué índices serán actualizados.

---

# 12. Grafo de memoria

## 12.1. Objetivo

Permitir que el usuario explore relaciones, no obligarlo a entender una base de datos.

## 12.2. Reglas de visualización

- Máximo inicial configurable de nodos.
- Profundidad 2–3.
- Filtros por tipo y relación.
- Búsqueda por texto.
- Zoom y pan.
- Selección de nodo.
- Inspector lateral.
- Modo lista alternativo.
- Indicador de subgrafo truncado.

## 12.3. Nodos

| Tipo | Color sugerido | Icono conceptual |
|---|---|---|
| Persona | cyan | rostro/terminal |
| Proyecto | violeta | módulo |
| Tarea | amber | checklist |
| Recordatorio | amarillo | reloj |
| Preferencia | verde | ajuste |
| Documento | azul | archivo |
| Evento | magenta | calendario |
| Agente | blanco/cyan | golem |

## 12.4. Interacción

- Click: seleccionar.
- Doble click: abrir detalle.
- Arrastrar: cambiar posición local.
- Shift + click: seleccionar varios.
- Teclado: recorrer nodos.
- Escape: cerrar inspector.

## 12.5. Rendimiento

- No dibujar todo el grafo en cada actualización.
- Virtualizar o limitar nodos.
- Usar Canvas/WebGL solo si SVG no alcanza.
- Reducir animación de líneas.
- Mantener fallback textual.

---

# 13. Agentes y mascotas

## 13.1. Selector de agente

Cada tarjeta muestra:

- Nombre.
- Mascota.
- Función.
- Modelo.
- Estado.
- Skills activas.
- Herramientas autorizadas.
- Nivel de autonomía.

## 13.2. Agentes iniciales

```text
VNBOT Core       → asistente general
Archivista       → memoria y recuperación
Beacon           → recordatorios
Navigator        → calendario y agenda
Forge            → creatividad y proyectos
Sentinel         → seguridad y permisos
Scout            → investigación
```

## 13.3. Mascotas por agente

Cada agente tiene una variante visual del golem definida en el spritesheet de agentes (`vnbot-golem-agent-spritesheet.png`). La familia comparte:

- Proporciones (base `golem_biped_64`).
- Lenguaje de armadura.
- Visor frontal.
- Píxeles de contorno.
- Escala.

Varía por agente:

| Elemento | Controlado por | Ejemplo |
|---|---|---|
| Accesorio | `accessory` | Beacon tiene antena, Forge tiene drones, Archivist tiene lentes |
| Color | `palette` | Beacon usa amber_graphite, Sentinel usa green_sentinel |
| Patrón del visor | `visor_pattern` | Beacon muestra señal de reloj, Sentinel muestra escudo |
| Pose base | `idle_animation` | Guardian biped estándar, Forge con drones en hover |

La definición completa de cada agente se encuentra en [Sección 19 — Sistema de mascota y sprites](#19-sistema-de-mascota-y-sprites).

Los emotes compactos (`vnbot-golem-ui-emotes.png`) se usan en la lista de agentes para indicar estado actual sin mostrar el sprite completo.
## 13.4. Estado del agente

La mascota puede aparecer en:

- Header.
- Chat.
- Panel Hoy.
- Selector de agentes.
- Vista de job.

No debe ocupar un espacio grande permanentemente en móvil.

---

# 14. Skills

## 14.1. Catálogo

Cada skill debe mostrar:

- Nombre.
- Descripción.
- Versión.
- Riesgo.
- Herramientas requeridas.
- Memoria requerida.
- Agentes compatibles.
- Fuente.
- Estado instalado/actualización.

## 14.2. Instalación

```text
Ver skill
  ↓
Revisar permisos
  ↓
Revisar origen/licencia
  ↓
Instalar
  ↓
Asignar a agente
  ↓
Probar en modo simulación
```

## 14.3. Vista de permisos

Debe ser legible para personas no técnicas:

```text
Esta skill puede:
✓ Leer memorias de trabajo
✓ Crear recordatorios
✕ Enviar emails
✕ Leer archivos personales
```

---

# 15. Integraciones y MCP

## 15.1. Card de integración

Debe mostrar:

- Nombre.
- Tipo de conexión.
- Estado.
- Último healthcheck.
- Scopes.
- Herramientas disponibles.
- Fecha de conexión.
- Botón de revocar.

## 15.2. Flujo de conexión

```text
Añadir integración
  ↓
Mostrar proveedor y riesgos
  ↓
Seleccionar transporte
  ↓
Autenticar
  ↓
Handshake
  ↓
Mostrar tools/resources
  ↓
Seleccionar scopes
  ↓
Confirmar
  ↓
Healthcheck
```

## 15.3. Estados

```text
not_configured
connecting
healthy
degraded
reauth_required
blocked
revoked
offline
```

## 15.4. Acciones de alto riesgo

Antes de activar `email.send`, `filesystem.write` o acciones equivalentes, mostrar:

- Datos que saldrán.
- Herramienta.
- Destino.
- Agente solicitante.
- Regla de confirmación.
- Cómo revocar.

---

# 16. Actividad y auditoría

## 16.1. Objetivo

Hacer visible lo que el asistente está haciendo y permitir investigar problemas.

## 16.2. Filtros

- Fecha.
- Agente.
- Tipo de operación.
- Estado.
- Integración.
- Riesgo.

## 16.3. Registro visual

```text
09:00  Beacon       Reminder created       success
09:02  Archivista   Memory indexed         success
09:05  Scout        MCP search             waiting confirmation
09:07  Core         LLM fallback heuristic warning
```

No se debe mostrar una API key, token ni contenido sensible completo.

---

# 17. Configuración

## 17.1. Categorías

```text
Cuenta
Bóveda y privacidad
Modelos LLM
Notificaciones
Agentes
Skills
Integraciones
Datos y exportación
Apariencia
Accesibilidad
Diagnóstico
```

## 17.2. Configuración de privacidad

Debe permitir elegir:

- Modo de procesamiento.
- Retención de audio.
- Proveedores permitidos.
- Memorias bloqueadas para cloud.
- Telemetría opcional.
- Auto-lock.
- Exportación.
- Borrado.

## 17.3. Diagnóstico

Mostrar:

- Versión.
- Estado de API.
- Estado de worker.
- Estado de base de datos.
- Estado de Redis.
- Estado de LLM.
- Estado de MCP.
- Espacio utilizado.
- Último backup.

---

# 18. Sistema de componentes

## 18.1. Componentes base

```text
PixelButton
PixelInput
PixelSelect
PixelCheckbox
PixelSwitch
PixelTabs
PixelTooltip
PixelModal
PixelDrawer
PixelToast
PixelBadge
PixelProgress
PixelDivider
PixelTable
PixelCard
```

## 18.2. Componentes de dominio

```text
MascotStateView
AgentCard
MemoryCard
MemoryInspector
GraphCanvas
GraphInspector
ReminderCard
ActionProposal
ConfirmationPanel
JobStatus
HealthStatus
PermissionMatrix
IntegrationCard
SkillCard
AuditEvent
```

## 18.3. Estados de cada componente

Cada componente debe definir:

- Default.
- Hover.
- Focus.
- Active.
- Disabled.
- Loading.
- Error.
- Empty.
- Offline.

---

# 19. Sistema de mascota y sprites

## 19.1. Assets disponibles

```text
assets-generated/
  vnbot-golem-mascot-variants.png     — 6 variantes conceptuales del golem (original)
  vnbot-golem-animation-sheet.png     — hoja conceptual de estados (original)
  vnbot-golem-agent-spritesheet.png   — 7 variantes de agentes con diferenciación visual
  vnbot-golem-state-spritesheet.png   — 10 estados del golem principal
  vnbot-golem-ui-emotes.png           — 12 emotes compactos para chat, toasts, badges
```

Referencia técnica: `VNBOT_SPRITESHEET_REFERENCE.md`.

Todas las imágenes son concept art y referencias de dirección. Antes de producción requieren:

1. Redibujar/limpiar píxeles.
2. Elegir resolución base.
3. Definir paleta bloqueada.
4. Separar cada frame.
5. Eliminar texto accidental dentro del sprite.
6. Probar sobre fondos claros y oscuros.
7. Crear metadata de licencia/origen.
8. Exportar PNG indexado.
9. Crear tests visuales.
10. Integrar con la máquina de estados real.

## 19.2. Familia de agentes

El spritesheet de agentes define siete variantes de la familia de golems:

| # | Agente | Rol | Paleta sugerida | Accesorio distintivo |
|---|---|---|---|---|
| 1 | Guardian | VNBOT Core, asistente general | cyan_graphite | Escudo/arma |
| 2 | Chat Assistant | Captura, conversación, onboarding | white_chat | Micrófono/antena simple |
| 3 | Archivist | Memoria, búsqueda, grafo | violet_archive | Lentes/cristal de datos |
| 4 | Beacon | Recordatorios y tareas | amber_graphite | Antena beacon/reloj |
| 5 | Navigator | Calendario y agenda | cyan_graphite | Brújula/ruta |
| 6 | Forge | Creatividad, proyectos, drones | magenta_forge | Drones/herramientas |
| 7 | Sentinel | Seguridad, bóveda, permisos | green_sentinel | Barrera/escudo reforzado |

La familia comparte: proporciones, lenguaje de armadura, visor, píxeles de contorno, escala. Varía: accesorio, color, patrón del visor, pose, efecto de estado.

### Asignación por pantalla

| Pantalla | Agente/Estado | Sprite |
|---|---|---|
| Landing | Guardian 128/64 | `golem-mascot-variants.png` |
| Login/bóveda | Sentinel | `golem-agent-spritesheet.png` |
| Chat | Chat Assistant / UI emotes | `golem-ui-emotes.png` |
| Hoy | Beacon | `golem-agent-spritesheet.png` |
| Memoria | Archivist | `golem-agent-spritesheet.png` |
| Grafo | Archivist / Navigator | `golem-agent-spritesheet.png` |
| Agentes | Todos | `golem-agent-spritesheet.png` |
| Skills | Forge / Core | `golem-agent-spritesheet.png` |
| MCP | Sentinel / Navigator | `golem-agent-spritesheet.png` |
| Jobs | Forge con drones | `golem-agent-spritesheet.png` |
| Errores | Estado error | `golem-state-spritesheet.png` |
| Offline | Estado offline | `golem-state-spritesheet.png` |
| Sleep/idle | Estado sleeping | `golem-state-spritesheet.png` |

## 19.3. Sistema de rendering procedural

Cada agente se define por datos, no por una imagen rígida. El renderer ensambla el sprite a partir de capas:

```json
{
  "agent_id": "beacon",
  "base_template": "golem_biped_64",
  "palette": "amber_cyan",
  "visor_pattern": "clock_signal",
  "accessory": "beacon_antenna",
  "idle_animation": "hover_low",
  "states": ["idle", "thinking", "processing", "success", "error"]
}
```

### 19.3.1. Capas del renderer

```text
background       — fondo transparente o color del contenedor
shadow           — sombra proyectada bajo el golem
body             — cuerpo base del golem (biped, hover, sentinel, archivist)
armor            — placas y segmentos de armadura
visor            — zona visual frontal (cambia por estado)
accessories      — elementos distintivos del agente (antena, escudo, lentes, drones)
particles        — efectos de partículas limitados
state_overlay    — overlay de color por estado (verde éxito, rojo error, etc.)
```

### 19.3.2. Plantillas base

```text
golem_biped_16    — icono pequeño (16×16 px)
golem_biped_32    — chat compacto (32×32 px)
golem_biped_64    — tarjetas y uso estándar (64×64 px)
golem_biped_128   — onboarding y hero (128×128 px)
golem_hover_64    — variantes flotantes
golem_sentinel_64 — variante centinela
golem_archivist_64 — variante archivista
```

### 19.3.3. Paletas

```text
cyan_graphite     — Guardian, Navigator (principal)
amber_graphite    — Beacon (recordatorios)
violet_archive    — Archivist (memoria)
magenta_forge     — Forge (creatividad)
green_sentinel    — Sentinel (seguridad)
white_chat        — Chat Assistant (conversación)
red_error         — estado de error (no es un agente, es un overlay)
```

## 19.4. Estados de la mascota

### Tabla completa de estados

| Estado | Trigger del backend | Visual del visor | Pose | Emote UI |
|---|---|---|---|---|
| `idle` | Sin operación activa | Cyan estable | Neutro, respiración sutil | neutral |
| `listening` | Captura de audio/entrada activa | Señal pulsante | Ligeramente inclinado hacia adelante | listening |
| `thinking` | Clasificación de intención o recuperación | Puntos en desplazamiento | Postura compacta | thinking |
| `processing` | Job activo ejecutándose | Anillo/indicador multicolor | Pose activa, posibles partículas | loading |
| `waiting_confirmation` | Propuesta pendiente de usuario | Amber estable | Pose de espera, brazos abajo | curious |
| `success` | Operación completada | Verde/cyan flash corto | Pose abierta, satisfactoria | confirmed / happy |
| `warning` | Resultado parcial o configuración necesaria | Amber intermitente limitado | Postura alerta suave | warning |
| `error` | Job fallido o error del sistema | Rojo, luego quieto | Postura de alerta | error |
| `offline` | Sin conexión al servidor | Visor apagado, sin brillo | Pose inactiva | offline |
| `sleeping` | Baja actividad prolongada o pausa | Indicador de reposo lento | Pose compacta, reducida | sleepy |

### Tipo del estado

```typescript
type MascotState =
  | 'idle'
  | 'listening'
  | 'thinking'
  | 'processing'
  | 'waiting_confirmation'
  | 'success'
  | 'warning'
  | 'error'
  | 'offline'
  | 'sleeping';
```

### Componente React

```tsx
<MascotStateView
  agent="beacon"
  state="processing"
  size={64}
  reducedMotion={prefersReducedMotion}
/>
```

El componente recibe el estado desde el store/stream de operaciones del backend. Nunca se anima de forma autónoma o aleatoria.

## 19.5. Emotes UI

El sheet de UI emotes contiene doce variaciones compactas para contextos donde el sprite completo no cabe:

- Chat: emotes dentro de burbujas de mensaje.
- Toasts: emotes junto a notificaciones breves.
- Badges: emotes como iconos de estado en cards.
- Notificaciones: emotes en el centro de notificación push.
- Lista de agentes: emote pequeño junto al nombre del agente.
- Mensajes de estado: emote junto a texto de estado del sistema.

### Lista de emotes

```text
neutral       — sin operación, reposo
happy         — éxito, confirmación positiva
curious       — propuesta generada, esperando input
focused       — procesamiento activo
listening     — captura de audio
thinking      — clasificación o recuperación
loading       — espera de backend
confirmed     — usuario confirmó acción
warning       — resultado parcial o atención
error         — fallo operativo
offline       — sin conexión
sleepy        — inactividad prolongada
```

Los emotes se usan en resolución 16×16 o 32×32. No requieren animación; son frames estáticos que se intercambian según el estado.

## 19.6. Resoluciones

```text
16×16   icono pequeño, emotes, badges, favicon
32×32   chat compacto, lista de agentes, notificaciones
64×64   tarjetas, panel Hoy, inspector
96×96   inspector detallado, vista de agente activo
128×128 onboarding, hero, landing
```

Escalado obligatorio: `image-rendering: pixelated` (nearest-neighbor). Nunca blur, nunca interpolación bilinear. Movimiento en píxeles enteros.

## 19.7. Animación

### Frames por estado

- Idle: 2–4 frames (respiración sutil).
- Listening: 2 frames (visor pulsante).
- Thinking: 2–3 frames (visor con desplazamiento).
- Processing: 3–6 frames (anillo/indicador + partículas).
- Waiting confirmation: 1–2 frames (amber estable, opcional pulso lento).
- Success: 2 frames (flash corto).
- Warning: 2 frames (amber intermitente).
- Error: 2 frames (rojo breve, luego quieto — no flashes rápidos continuos).
- Offline: 1 frame (estático).
- Sleeping: 1–2 frames (indicador de reposo muy lento).

### Overlay de partículas

Limitado a los estados `processing` y `success`. Nunca más de 5–8 partículas simultáneas. Las partículas usan la paleta del agente activo.

### Reglas de animación

- Escalado nearest-neighbor obligatorio.
- Sin blur ni suavizado.
- Sin interpolación bilinear.
- Movimiento en píxeles enteros (integer positioning).
- Pausar la animación cuando el componente no esté visible (`IntersectionObserver`).
- Respetar `prefers-reduced-motion: reduce` — mostrar frame estático del estado.
- Proporcionar siempre un frame estático como fallback.
- No utilizar flashes rápidos en error/warning (riesgo de accesibilidad, fotosensibilidad).
- Duración de ciclo idle: 2–4 segundos.
- Duración de ciclo processing: 1–2 segundos.

## 19.8. Correspondencia con estados del backend

Los estados visuales de la mascota se mapean directamente a los estados operativos del backend. Ver [App Flow — Estados globales](./06-APP-FLOW-VNBOT.md) para el detalle de transiciones.

| Estado App Flow | Estado mascota | Notas |
|---|---|---|
| `READY` | `idle` | Estado por defecto |
| `DEGRADED_LLM` | `warning` | Fallback activo |
| `OFFLINE` | `offline` | Sin conexión |
| `SYNC_PENDING` | `processing` | Sincronizando |
| `LOCKED` | `sleeping` | Bóveda cerrada |
| Chat: enviando | `listening` | Capturando input |
| Chat: interpretando | `thinking` | LLM o heurística |
| Chat: ejecutando | `processing` | Job activo |
| Chat: propuesta | `waiting_confirmation` | Esperando al usuario |
| Operación: éxito | `success` | Completado |
| Operación: fallo | `error` | Con mensaje de recuperación |

---



## 20.1. Grabación

Antes de grabar:

- Mostrar permiso de micrófono.
- Indicar si la transcripción será local o externa.
- Mostrar duración.
- Mostrar botón de cancelar.

Durante:

- Estado `listening`.
- Medidor simple de audio.
- Duración visible.
- Detener y pausar.

Después:

- Estado `transcribing`.
- Transcripción editable.
- Reproducir audio si se conserva.
- Confirmar acción resultante.

## 20.2. Errores

- Micrófono denegado.
- Audio vacío.
- Formato no soportado.
- Modelo no disponible.
- Transcripción incompleta.
- Conexión perdida.

Cada error debe ofrecer una alternativa: escribir, reintentar o guardar audio sin procesar.

---

# 21. Accesibilidad

## 21.1. Teclado

- Todo control debe tener foco.
- Orden de tabulación lógico.
- Escape cierra modal/drawer.
- Enter confirma solo cuando es seguro.
- Atajos no deben interferir con escritura.

## 21.2. Lectores de pantalla

- `aria-label` para iconos.
- Texto alternativo para mascota informativa.
- Estados anunciados mediante live regions.
- El grafo tiene una vista de lista equivalente.
- Los colores se acompañan de texto.

## 21.3. Movimiento

Con `prefers-reduced-motion`:

- Desactivar parallax.
- Desactivar loops decorativos.
- Mantener solo cambios de estado necesarios.
- No usar flashes rápidos.

## 21.4. Contraste

Las líneas HUD decorativas pueden tener contraste bajo; los controles, texto, estados y focus rings no.

---

# 22. Performance UI

## 22.1. Assets

- Sprite sheets en lugar de cientos de imágenes.
- PNG indexado o WebP donde no se pierda nitidez.
- Sin interpolación borrosa.
- Lazy loading.
- Precarga solo de mascota activa.
- Versionado por hash.

## 22.2. Listas

- Virtualización para memorias, logs y recordatorios.
- Paginación cursor-based.
- No cargar todo el historial en el cliente.

## 22.3. Grafo

- Límite de nodos.
- Memoización de layout.
- Actualizaciones por frame agrupadas.
- Pausar si no es visible.
- Fallback SVG/lista.

## 22.4. Animaciones

- Preferir CSS transform/opacity.
- No animar grandes fondos constantemente.
- No generar Canvas en cada render de React.
- Liberar listeners al desmontar.

---

# 23. Estados globales de experiencia

La aplicación debe contemplar estados que no son solo “cargando” o “error”:

```text
first_run
locked
ready
offline
sync_pending
degraded_llm
degraded_worker
mcp_reauth_required
empty_state
partial_data
maintenance
```

Cada estado debe tener:

- Mensaje.
- Acción disponible.
- Impacto explicado.
- Mascota adecuada.
- Alternativa manual.

---

# 24. Microcopy

## 24.1. Principios

- Directo.
- Humano.
- No exagerar capacidades.
- No decir “hecho” si solo se creó una propuesta.
- Explicar límites sin lenguaje legalista innecesario.

## 24.2. Ejemplos

### Correcto

> Preparé un recordatorio para el viernes 17 de julio a las 09:00. Confírmalo para activarlo.

### Incorrecto

> Listo, me encargaré de todo.

### Error

> No pude enviar la notificación porque Telegram necesita reconectar. El recordatorio sigue guardado y puedes reintentar.

### Privacidad

> Esta acción usaría el modelo remoto seleccionado. El texto enviado no incluye memorias marcadas como secretas.

---

# 25. Diseño de la landing de GitHub Pages

## Secciones

1. Hero con golem principal.
2. Promesa: memoria, recordatorios y agentes bajo control.
3. Demo interactiva simulada.
4. Vista del panel.
5. Vista del grafo.
6. Mascotas y estados.
7. Instalación local.
8. Docker.
9. APK/Desktop Releases.
10. Privacidad.
11. Arquitectura.
12. GitHub y contribución.

## Restricciones

- No pedir API key.
- No guardar datos reales.
- No depender de backend para cargar.
- Mostrar claramente “Demo simulada” cuando corresponda.
- Mantener carga rápida.

---

# 26. Diseño de notificaciones

## Notificación estándar

```text
VNBOT · Beacon
Revisar el presupuesto
Hoy, 09:00
[Completar] [Posponer]
```

## Notificación de acción pendiente

```text
VNBOT necesita tu confirmación
Crear evento en Google Calendar
[Ver detalles] [Confirmar] [Cancelar]
```

## Reglas

- No incluir secretos.
- No exponer contenido sensible en pantalla bloqueada.
- Permitir ocultar previsualización.
- Permitir escoger canal.

---

# 27. Pruebas UX

## 27.1. Pruebas de usabilidad

- Crear primer recordatorio.
- Corregir fecha incorrecta.
- Encontrar una memoria.
- Olvidar una memoria.
- Identificar qué agente está activo.
- Comprender un permiso MCP.
- Recuperarse de un error de conexión.
- Exportar datos.

## 27.2. Criterios

- El usuario entiende la acción antes de confirmarla.
- El usuario distingue memoria de recordatorio.
- El usuario sabe cuándo la IA está trabajando.
- El usuario encuentra una alternativa si un servicio falla.
- El usuario puede operar sin entender MCP.
- El usuario avanzado puede inspeccionar detalles técnicos.

## 27.3. Pruebas visuales

- Capturas por breakpoint.
- Contraste.
- Pixel scaling.
- Estado de sprites.
- Fallback sin WebGL.
- Reduced motion.
- Pantalla pequeña.
- Tema de alto contraste.

---

# 28. Requisitos para assets de alta calidad

Cada asset debe registrar:

```text
asset_id
nombre
variante
resolución
frames
paleta
modelo/origen
prompt
revisor
licencia
checksum
fecha
```

Proceso:

```text
Concepto generado
→ selección
→ limpieza manual
→ paleta limitada
→ separación de frames
→ escalado nearest-neighbor
→ pruebas en UI
→ inventario de licencia
→ exportación
```

Las imágenes con watermarks o procedentes de bancos de stock no se utilizarán en producción.

## 28.5. Inventario de spritesheets

| Archivo | Tipo | Contenido | Estado | Uso |
|---|---|---|---|---|
| `vnbot-golem-mascot-variants.png` | Concept art | 6 variantes del golem (guardián, amistoso, analista, drones, centinela, archivista) | Prototipo — requiere limpieza | Referencia de dirección artística |
| `vnbot-golem-animation-sheet.png` | Concept art | Hoja de estados conceptuales original | Prototipo — requiere limpieza | Referencia de animación original |
| `vnbot-golem-agent-spritesheet.png` | Concept art | 7 agentes diferenciados con accesorios y paletas | Prototipo — requiere separación de frames | Definición de variante por agente |
| `vnbot-golem-state-spritesheet.png` | Concept art | 10 estados del golem principal (idle→sleeping) | Prototipo — requiere separación de frames | Definición de estados visuales |
| `vnbot-golem-ui-emotes.png` | Concept art | 12 emotes compactos para chat, toasts, badges | Prototipo — requiere separación de frames | Emotes UI compactos |

Todos requieren antes de producción: limpieza manual, separación de frames individuales, revisión de paleta, metadata de licencia/origen, pruebas sobre fondos claros y oscuros, y exportación en formato PNG indexado.

---

# 29. Criterios de aceptación UI/UX

El diseño cumple la primera versión cuando:

1. El usuario entiende qué puede hacer VNBOT al abrirlo.
2. Puede crear un recordatorio sin documentación.
3. Ve claramente cuándo una acción necesita confirmación.
4. Puede distinguir agente, skill y herramienta.
5. Puede acceder al detalle de una memoria.
6. Puede consultar el grafo en modo visual o lista.
7. Puede trabajar en móvil y desktop.
8. La mascota refleja los estados reales.
9. La interfaz funciona sin blur ni efectos pesados.
10. Las animaciones respetan reduced motion.
11. Los textos son legibles.
12. Los errores ofrecen acciones concretas.
13. La información privada no aparece accidentalmente en notificaciones.
14. La demo de GitHub Pages es comprensible sin backend.
15. El usuario avanzado puede revisar actividad y permisos.

---

# 30. Orden de implementación visual

## Fase 1 — Sistema base

- Tokens.
- Tipografía.
- Layout.
- Responsive.
- Componentes base.
- Tema oscuro.
- Accesibilidad.

## Fase 2 — Mascota

- Golem principal.
- Escalas.
- Estados.
- Sprite sheet.
- Integración con WebSocket/polling de operaciones.

## Fase 3 — Vistas núcleo

- Onboarding.
- Hoy.
- Chat.
- Memoria.
- Recordatorios.

## Fase 4 — Grafo y agentes

- Grafo limitado.
- Inspector.
- Selector de agentes.
- Skills.
- Permisos.

## Fase 5 — Integraciones y diagnóstico

- MCP.
- Healthchecks.
- Actividad.
- Logs.
- Integraciones.

## Fase 6 — Pulido

- Animaciones.
- Temas.
- High contrast.
- Reduced motion.
- Optimización de assets.
- Pruebas en dispositivos reales.

---

# 31. Decisiones abiertas

1. Tipografía pixel definitiva.
2. Sistema de iconos propio o adaptación de una librería compatible.
3. SVG, Canvas o WebGL como renderer principal del grafo.
4. Navegación inferior definitiva para Android.
5. Número máximo de mascotas disponibles en el primer release.
6. Si las variantes de agentes se podrán desbloquear o serán configurables desde el inicio.
7. Soporte de temas personalizados en el MVP.
8. Estrategia de sonidos opcionales de interfaz.
9. Editor visual de paletas.
10. Sistema de packs de assets comunitarios.

---

# 32. Conclusión

La interfaz de VNBOT debe comunicar que el usuario posee una estación personal de memoria y agentes. El pixel art y el HUD cyberpunk aportan identidad, pero la experiencia debe seguir siendo clara, accesible y funcional.

La mascota será una parte operativa del sistema: mostrará estados reales y ayudará a que el usuario comprenda si VNBOT está escuchando, pensando, procesando, esperando aprobación, completando o fallando.

El diseño final se basará en:

```text
Golem original
+ sprites de alta calidad
+ HUD modular
+ estados verificables
+ agentes visualmente diferenciados
+ grafo comprensible
+ acciones explicadas
+ accesibilidad
+ rendimiento multiplataforma
```

La regla visual central es:

> La estética puede hacer que VNBOT sea memorable; la claridad debe hacer que sea confiable.

---

# 33. Requisitos de accesibilidad

### 33.1. Estándar y nivel

VNBOT debe cumplir **WCAG 2.2 nivel AA** como mínimo en todas sus interfaces. El nivel AAA es aspiracional para:

- Chat (interacción principal).
- Recordatorios (información temporal crítica).
- Confirmaciones de acciones irreversibles.

### 33.2. Métricas concretas por componente

| Componente | Requisito de contraste | Tamaño mínimo | Touch target | Notas |
|---|---|---|---|---|
| Texto de chat | 4.5:1 (AA) | 14px / 16sp | N/A | Fuente legible en modo claro y oscuro |
| Labels de estado (mascota) | 3:1 (AA large text) | 12px | N/A | Solo informativo, no interactivo |
| Botones de acción | 4.5:1 fondo/texto | 14px | 44×44px | Focus visible obligatorio |
| Paneles HUD | 3:1 borde/fondo | N/A | N/A | Decorativo + informativo |
| Inputs de texto | 4.5:1 | 16px | 48×44px | Label asociado |
| Cards de memoria | 3:1 texto/fondo card | 14px | N/A | No es interactivo directamente |
| Grafo de nodos | 3:1 nodo/fondo | Label 12px | 24×24px mínimo | Navegable por teclado |
| Botón de confirmación de acción | 4.5:1 | 16px | 48×48px | Contraste aumentado por seguridad |

### 33.3. Navegación por teclado

Todas las funciones de VNBOT deben ser accesibles sin ratón:

- `Tab` / `Shift+Tab`: navegar entre elementos interactivos.
- `Enter` / `Space`: activar botones y links.
- `Escape`: cerrar modales, cancelar acciones.
- `Arrow keys`: navegar dentro del grafo, listas y menús.
- Atajos de teclado documentados en una página de ayuda accesible con `?`.

### 33.4. Screen readers

- Todos los componentes interactivos deben tener `aria-label` o `aria-labelledby`.
- Los estados de la mascota deben tener `aria-live="polite"` para anunciar cambios.
- Las notificaciones de recordatorio deben usar `role="alert"`.
- El grafo debe tener una alternativa en lista (table o description) para lectores de pantalla.
- Los modales deben atrapar el foco y devolverlo al elemento trigger al cerrar.

### 33.5. Reduced motion

VNBOT debe respetar `prefers-reduced-motion: reduce`:

- Desactivar animaciones de sprites de la mascota (mostrar estado estático).
- Desactivar transiciones de paneles.
- Desactivar animaciones de entrada/salida de elementos.
- Mantener la funcionalidad completa sin animación.
- Los estados de la mascota se comunican mediante texto, no solo animación.

### 33.6. Pixel art y accesibilidad en móviles

El lenguaje visual de VNBOT (pixel art, HUD cyberpunk) presenta desafíos específicos:

- **Sprites:** El pixel art debe tener resolución suficiente para ser reconocible en pantallas de 320px de ancho. Mínimo 32×32px para la mascota, 64×64px recomendado.
- **Bordes angulares HUD:** No deben crear trampas de foco ni interferir con touch targets. Los bordes decorativos se implementan con `pointer-events: none`.
- **Paneles con alta densidad:** La vista de uso diario debe ser menos densa que las referencias de HUD. Los paneles técnicos se reservan para Actividad, Integraciones y Diagnóstico.
- **Escalado:** El pixel art usa `image-rendering: pixelated` (nearest-neighbor) pero los textos del UI usan fuentes vectoriales para legibilidad a cualquier resolución.
- **Contraste en modo oscuro:** La paleta dark navy/cyan debe verificar contraste AA para todas las combinaciones de texto sobre fondo.

### 33.7. Plan de auditoría

| Momento | Tipo de auditoría | Herramienta |
|---|---|---|
| Cada PR | Automática (axe-core) | CI pipeline |
| Antes de cada release minor | Manual rápida | Lighthouse + teclado |
| Antes de cada release major | Manual completa | NVDA + VoiceOver + keyboard |
| Antes de v1.0 | Con usuarios reales | Usuarios con discapacidades |
| Trimestral (post v1.0) | Re-auditoría | Completa |

### 33.8. Tokens de diseño de accesibilidad

Los design tokens deben incluir variantes de contraste:

```text
--color-text-primary: #E0E7FF (contra #0F172A = 14.3:1 ✓)
--color-text-secondary: #94A3B8 (contra #0F172A = 6.1:1 ✓)
--color-accent-cyan: #22D3EE (contra #0F172A = 10.8:1 ✓)
--color-accent-magenta: #F472B6 (contra #0F172A = 6.8:1 ✓)
--color-accent-amber: #FBBF24 (contra #0F172A = 10.2:1 ✓)
--color-danger: #EF4444 (contra #0F172A = 5.5:1 ✓)
--color-success: #34D399 (contra #0F172A = 11.3:1 ✓)
```

Cualquier combinación de color nueva debe verificarse contra https://webaim.org/resources/contrastchecker/ antes de merge.

---

# 34. Consideraciones de rendimiento visual

### 34.1. Sprite sheets

- Las animaciones de la mascota se cargan como sprite sheets, no como archivos individuales.
- Lazy loading para sprites que no están en la vista actual.
- Solo se carga la variante del agente activo.
- Los sprites se precargan tras el primer render, no antes (no bloquear LCP).

### 34.2. Paneles HUD en pantallas pequeñas

- En pantallas < 375px de ancho, los paneles HUD se simplifican: bordes menos complejos, menos indicadores.
- Los paneles técnicos (Actividad, Healthcheck) no están disponibles en la navegación móvil por defecto; se acceden mediante "Modo avanzado".
- El grafo en móvil se muestra como lista por defecto, con opción de vista visual.

### 34.3. Performance budgets

| Métrica | Objetivo | Verificación |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s en móvil | Lighthouse CI |
| CLS (Cumulative Layout Shift) | < 0.1 | Lighthouse CI |
| INP (Interaction to Next Paint) | < 200ms | Lighthouse CI |
| Tamaño total de sprites | < 200KB comprimidos | Build script |
| Tamaño total de JS | < 300KB gzipped (MVP) | Build script |
| FPS con animaciones | > 30fps en móvil gama media | Manual en dispositivos de referencia |
