# VNBOT — Referencia de spritesheets

## Archivos

- `vnbot-golem-agent-spritesheet.png`
- `vnbot-golem-state-spritesheet.png`
- `vnbot-golem-ui-emotes.png`

Estos spritesheets son referencias visuales para la recreación procedural mediante código. No deben tratarse como el sistema final de animación ni como una fuente de verdad de píxeles individuales.

---

## 1. Agent spritesheet

Archivo: `vnbot-golem-agent-spritesheet.png`

Contiene siete variantes de la familia de golems:

1. **Guardian** — mascota principal, VNBOT Core.
2. **Chat Assistant** — captura, conversación y onboarding.
3. **Archivist** — memoria, búsqueda y grafo.
4. **Beacon** — recordatorios y tareas.
5. **Navigator** — calendario y agenda.
6. **Forge** — creatividad, proyectos y drones.
7. **Sentinel** — seguridad, bóveda y permisos.

### Uso procedural

Cada agente debe definirse por datos, no por una imagen rígida:

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

---

## 2. State spritesheet

Archivo: `vnbot-golem-state-spritesheet.png`

Contiene diez estados del golem principal:

1. Idle.
2. Listening.
3. Thinking.
4. Processing.
5. Waiting for confirmation.
6. Success.
7. Warning.
8. Error.
9. Offline.
10. Sleeping.

### Tabla de estados

| Estado | Backend | Visual |
|---|---|---|
| idle | Sin operación activa | Visor cyan estable |
| listening | Captura de audio/entrada | Visor con señal |
| thinking | Clasificación o recuperación | Visor con puntos |
| processing | Job activo | Anillo/indicador multicolor |
| waiting_confirmation | Propuesta pendiente | Visor amber |
| success | Operación completada | Visor verde y pose abierta |
| warning | Resultado parcial/configuración | Amber/partículas limitadas |
| error | Job fallido | Rojo, postura de alerta |
| offline | Sin conexión | Visor apagado |
| sleeping | Baja actividad | Pose compacta/indicador de reposo |

La implementación final debe evitar texto incrustado dentro del sprite. Los estados deben tener una etiqueta accesible fuera de la imagen.

---

## 3. UI emotes sheet

Archivo: `vnbot-golem-ui-emotes.png`

Contiene doce emotes compactos para:

- Chat.
- Toasts.
- Badges.
- Notificaciones.
- Lista de agentes.
- Mensajes de estado.

Estados conceptuales:

```text
neutral
happy
curious
focused
listening
thinking
loading
confirmed
warning
error
offline
sleepy
```

---

## 4. Convención procedural

## 4.1. Capas

El renderer debe separar:

```text
background
shadow
body
armor
visor
accessories
particles
state_overlay
```

## 4.2. Plantillas

```text
golem_biped_16
golem_biped_32
golem_biped_64
golem_biped_128
golem_hover_64
golem_sentinel_64
golem_archivist_64
```

## 4.3. Paletas

```text
cyan_graphite
amber_graphite
violet_archive
magenta_forge
green_sentinel
white_chat
red_error
```

## 4.4. Estados como datos

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

El componente recibe el estado desde el store/stream de operaciones:

```tsx
<MascotStateView
  agent="beacon"
  state="processing"
  size={64}
  reducedMotion={prefersReducedMotion}
/>
```

---

## 5. Animación recomendada

No se debe animar únicamente la imagen completa. Se recomienda combinar:

- 2–4 frames de idle.
- 2 frames de visor pulsante.
- 3–6 frames de processing.
- 2 frames de success.
- 2 frames de warning.
- 2 frames de error.
- Overlay de partículas limitado.

### Reglas

- Escalado nearest-neighbor.
- Sin blur.
- Sin interpolación bilinear.
- Movimiento en píxeles enteros.
- Pausar cuando no esté visible.
- Respetar `prefers-reduced-motion`.
- Proporcionar frame estático.
- No utilizar flashes rápidos en error/warning.

---

## 6. Producción final

Estas imágenes son concept art y referencias de dirección. Antes de integrarlas como recursos finales:

1. Redibujar/limpiar píxeles.
2. Elegir resolución base.
3. Definir paleta bloqueada.
4. Separar cada frame.
5. Eliminar texto accidental dentro del sprite.
6. Probar sobre fondos claros y oscuros.
7. Crear metadata de licencia/origen.
8. Exportar PNG indexado o formato acordado.
9. Crear tests visuales.
10. Integrar con la máquina de estados real.

---

## 7. Correspondencia con VNBOT

| Área | Sprite recomendado |
|---|---|
| Landing | Guardian 128/64 |
| Login/bóveda | Sentinel |
| Chat | Chat Assistant / UI emotes |
| Hoy | Beacon |
| Memoria | Archivist |
| Grafo | Archivist / Navigator |
| Agentes | Todos |
| Skills | Forge / Core |
| MCP | Sentinel / Navigator |
| Jobs | Forge con drones |
| Errores | State error |
| Offline | State offline |
| Sleep/idle | State sleeping |
