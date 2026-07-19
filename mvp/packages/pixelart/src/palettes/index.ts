/**
 * VNBOT Pixelart — 7 Agent Palettes
 * Source: docs/05-DISENO-UI-UX §13.2 + VNBOT_SPRITESHEET_REFERENCE §4.3
 *
 * Each palette defines: primary, secondary, accent, visor, shadow, outline
 * Visor color changes per state (computed in renderers/renderVisor)
 */

import type { Palette, PaletteName } from '../engine/types';

export const PALETTES: Record<PaletteName, Palette> = {
  cyan_graphite: {
    name: 'cyan_graphite',
    primary: '#20DCE8', // cyan — Guardian, Navigator
    secondary: '#2A6F8E',
    accent: '#4D9DFF',
    visor: '#20DCE8',
    shadow: 'rgba(7, 10, 18, 0.7)',
    outline: '#0A1020',
  },
  white_chat: {
    name: 'white_chat',
    primary: '#ECF6FF', // near-white — Chat Assistant
    secondary: '#91A9BE',
    accent: '#20DCE8',
    visor: '#20DCE8',
    shadow: 'rgba(7, 10, 18, 0.6)',
    outline: '#0A1020',
  },
  violet_archive: {
    name: 'violet_archive',
    primary: '#8A6CFF', // violet — Archivist
    secondary: '#4D9DFF',
    accent: '#D94BE3',
    visor: '#8A6CFF',
    shadow: 'rgba(7, 10, 18, 0.7)',
    outline: '#0A1020',
  },
  amber_graphite: {
    name: 'amber_graphite',
    primary: '#FFC83D', // amber — Beacon
    secondary: '#2A6F8E',
    accent: '#FF5C6D',
    visor: '#FFC83D',
    shadow: 'rgba(7, 10, 18, 0.7)',
    outline: '#0A1020',
  },
  magenta_forge: {
    name: 'magenta_forge',
    primary: '#D94BE3', // magenta — Forge
    secondary: '#8A6CFF',
    accent: '#FFC83D',
    visor: '#D94BE3',
    shadow: 'rgba(7, 10, 18, 0.7)',
    outline: '#0A1020',
  },
  green_sentinel: {
    name: 'green_sentinel',
    primary: '#5BDF82', // green — Sentinel
    secondary: '#20DCE8',
    accent: '#FFC83D',
    visor: '#5BDF82',
    shadow: 'rgba(7, 10, 18, 0.7)',
    outline: '#0A1020',
  },
  red_error: {
    name: 'red_error',
    primary: '#FF5C6D', // red — state overlay only (not an agent)
    secondary: '#8A6CFF',
    accent: '#FFC83D',
    visor: '#FF5C6D',
    shadow: 'rgba(7, 10, 18, 0.8)',
    outline: '#0A1020',
  },
};

/**
 * Get a palette by name. Throws if unknown — caller must validate.
 */
export function getPalette(name: PaletteName): Palette {
  const p = PALETTES[name];
  if (!p) throw new Error(`Unknown palette: ${name}`);
  return p;
}
