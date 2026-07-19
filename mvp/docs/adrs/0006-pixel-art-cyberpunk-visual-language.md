# ADR-0006: Pixel art cyberpunk as visual language (not glassmorphism)

## Estado

Aceptada

## Contexto

VNBOT necesita un lenguaje visual distintivo que:

- Comunique "asistente técnico, confiable, controlable" (no consumer-genérico tipo iOS).
- Sea accesible (alto contraste, legible, sin dependencia de motion).
- Rinda bien en dispositivos móviles de gama media.
- Tenga identidad propia (no copie marcas ni assets existentes).
- Sea consistente entre PWA, APK, desktop, CLI.

Las alternativas eran:

1. **Glassmorphism + blur** — estética iOS/macOS, requiere GPU, mal rendimiento en mobile.
2. **Material Design 3** — estética Google, genérico, no distintivo.
3. **Pixel art cyberpunk HUD** — alineado con la mascota golem informático, alto contraste natural, perf bueno (nearest-neighbor scaling).
4. **Flat minimalista** — limpio pero genérico, no diferencia.

## Decisión

**Pixel art cyberpunk HUD como lenguaje visual principal.** Especificaciones:

- **Mascota:** Golem informático original (no copiar personajes existentes) con 7 variantes por agente.
- **Paleta canónica:** dark navy (#0A1020) + cyan (#20DCE8) + magenta (#D94BE3) + violet (#8A6CFF) + amber (#FFC83D) + green (#5BDF82) + red (#FF5C6D).
- **Tipografía:** Press Start 2P (títulos pixel) + Space Grotesk (display) + Inter (body) + JetBrains Mono (logs).
- **Componentes:** PixelPanel, HudFrame, ActionCard, MemoryCard, AgentCard con clip-path angular.
- **Animación:** nearest-neighbor (`image-rendering: pixelated`), movimiento en píxeles enteros, sin blur ni bilinear.
- **Accesibilidad:** respeta `prefers-reduced-motion`, sin flashes rápidos (fotosensibilidad), contraste WCAG 2.2 AA.

**PROHIBIDO:**

- Glassmorphism (`backdrop-filter: blur()`).
- Blur como estructura principal.
- Soft shadows tipo iOS.
- Copiar personajes o interfaces reconocibles.
- Usar imágenes con watermarks como assets finales.

## Consecuencias

- **Positivas**: Identidad distintiva, alto contraste natural (oscuro + cyan brillante), perf bueno, escala a cualquier resolución sin pixelación.
- **Negativas**: Estética polarizante (no mainstream), más trabajo de diseño (procedural pixelart engine).
- **Riesgos**: Pixel art mal ejecutado se ve amateur — mitigar con motor procedural bien estructurado (8 capas, PRNG + noise).

## Alternativas consideradas

1. **Glassmorphism** — descartada por perf en mobile y falta de identidad.
2. **Material 3** — descartada por genérico.
3. **Flat minimalista** — descartada por no distintivo.

## Referencias

- UI §2.4 (anti-patterns), §4 (palette), §19 (procedural sprite system)
- VISUAL_REFERENCES_AND_ANALYSIS.md (5 reference images analyzed)
- VNBOT_SPRITESHEET_REFERENCE.md (technical reference)
- ADR relacionado: ninguno (visual decision, no architectural)
