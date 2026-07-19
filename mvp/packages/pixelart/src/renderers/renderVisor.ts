/**
 * VNBOT Pixelart — Visor Renderer
 *
 * The visor is the frontal visual zone of the golem — it changes per state.
 * State → visor color + pattern mapping (per VNBOT_SPRITESHEET_REFERENCE §2):
 *
 *   idle                   → stable cyan
 *   listening              → pulsing signal
 *   thinking               → scrolling dots
 *   processing             → multicolor ring
 *   waiting_confirmation   → stable amber
 *   success                → green/cyan short flash
 *   warning                → blinking amber
 *   error                  → red then quiet
 *   offline                → visor off (no glow)
 *   sleeping               → slow rest indicator
 *
 * The visor is drawn at a fixed position on the head (top portion of body).
 */

import type { MascotState, Palette } from '../engine/types';

interface RenderVisorOptions {
  size: number;
  state: MascotState;
  palette: Palette;
  frame: number; // current frame index for animation
  seed: string;
}

const STATE_COLORS: Record<MascotState, string> = {
  idle: '#20DCE8', // cyan
  listening: '#20DCE8', // cyan (pulsing)
  thinking: '#8A6CFF', // violet (dots)
  processing: '#D94BE3', // magenta (ring)
  waiting_confirmation: '#FFC83D', // amber
  success: '#5BDF82', // green
  warning: '#FFC83D', // amber (blinking)
  error: '#FF5C6D', // red
  offline: '#1D465E', // dark
  sleeping: '#2A6F8E', // dim
};

export function renderVisor(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  opts: RenderVisorOptions,
): void {
  const { size, state, palette, frame } = opts;
  const color = state === 'idle' ? palette.visor : STATE_COLORS[state];

  // Visor position: top-center of the head (rows 2-3 of the 16-grid for 128px)
  // Center horizontally, vertically at ~15-25% from top
  const visorWidth = size * 0.4;
  const visorHeight = size * 0.1;
  const visorX = (size - visorWidth) / 2;
  const visorY = size * 0.18;

  ctx.save();
  ctx.imageSmoothingEnabled = false;

  // Outer glow (radial gradient) — skip if offline/sleeping for power-saving look
  if (state !== 'offline' && state !== 'sleeping') {
    const glowAlpha = computeGlowAlpha(state, frame);
    const gradient = ctx.createRadialGradient(
      size / 2,
      visorY + visorHeight / 2,
      0,
      size / 2,
      visorY + visorHeight / 2,
      visorWidth,
    );
    gradient.addColorStop(0, hexToRgba(color, glowAlpha));
    gradient.addColorStop(0.5, hexToRgba(color, glowAlpha * 0.4));
    gradient.addColorStop(1, hexToRgba(color, 0));
    ctx.fillStyle = gradient;
    ctx.fillRect(visorX - visorWidth / 2, visorY - visorHeight, visorWidth * 2, visorHeight * 3);
  }

  // Visor base (solid rectangle)
  ctx.fillStyle = color;
  ctx.fillRect(visorX, visorY, visorWidth, visorHeight);

  // Inner darker band for depth
  ctx.fillStyle = hexToRgba(palette.outline, 0.4);
  ctx.fillRect(visorX, visorY + visorHeight * 0.6, visorWidth, visorHeight * 0.4);

  // State-specific pattern overlay
  drawStatePattern(ctx, state, visorX, visorY, visorWidth, visorHeight, frame, color);

  ctx.restore();
}

function computeGlowAlpha(state: MascotState, frame: number): number {
  switch (state) {
    case 'idle':
      return 0.6;
    case 'listening':
      // Pulse: 0.4 → 0.9 → 0.4 over 2 frames
      return 0.4 + 0.5 * Math.abs(Math.sin(frame * Math.PI));
    case 'thinking':
      return 0.5;
    case 'processing':
      // Strong pulsing
      return 0.5 + 0.4 * Math.sin(frame * Math.PI * 0.5);
    case 'waiting_confirmation':
      return 0.7;
    case 'success':
      // Brief flash first frame, then steady
      return frame === 0 ? 0.95 : 0.6;
    case 'warning':
      // Slow blink
      return frame % 2 === 0 ? 0.7 : 0.2;
    case 'error':
      // Brief red flash, then quiet
      return frame === 0 ? 0.9 : 0.3;
    case 'offline':
      return 0;
    case 'sleeping':
      // Slow dim pulse
      return 0.2 + 0.15 * Math.sin(frame * Math.PI * 0.25);
  }
}

function drawStatePattern(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  state: MascotState,
  x: number,
  y: number,
  w: number,
  h: number,
  frame: number,
  color: string,
): void {
  ctx.save();

  switch (state) {
    case 'thinking': {
      // Three scrolling dots
      const dotSize = h * 0.3;
      for (let i = 0; i < 3; i++) {
        const offsetX = ((frame + i) % 4) * (w / 4) - w / 2;
        const dotX = x + w / 2 + offsetX - dotSize / 2;
        ctx.fillStyle = '#ECF6FF';
        ctx.fillRect(dotX, y + h / 2 - dotSize / 2, dotSize, dotSize);
      }
      break;
    }
    case 'processing': {
      // Multicolor ring (3 arcs)
      const cx = x + w / 2;
      const cy = y + h / 2;
      const r = h * 0.6;
      const colors = ['#20DCE8', '#D94BE3', '#FFC83D'];
      for (let i = 0; i < 3; i++) {
        const startAngle = (frame * Math.PI) / 3 + (i * 2 * Math.PI) / 3;
        ctx.strokeStyle = colors[i];
        ctx.lineWidth = h * 0.3;
        ctx.beginPath();
        ctx.arc(cx, cy, r, startAngle, startAngle + (Math.PI * 2) / 3);
        ctx.stroke();
      }
      break;
    }
    case 'listening': {
      // Signal bars (3 vertical bars with varying heights)
      const barWidth = w / 5;
      for (let i = 0; i < 3; i++) {
        const heightFactor = 0.4 + 0.6 * Math.abs(Math.sin(frame * Math.PI + i));
        const barH = h * heightFactor;
        ctx.fillStyle = '#ECF6FF';
        ctx.fillRect(x + (i + 1) * barWidth, y + h - barH, barWidth * 0.6, barH);
      }
      break;
    }
    case 'success': {
      // Checkmark
      ctx.strokeStyle = '#ECF6FF';
      ctx.lineWidth = h * 0.3;
      ctx.lineCap = 'square';
      ctx.beginPath();
      ctx.moveTo(x + w * 0.25, y + h / 2);
      ctx.lineTo(x + w * 0.45, y + h * 0.75);
      ctx.lineTo(x + w * 0.75, y + h * 0.25);
      ctx.stroke();
      break;
    }
    case 'warning': {
      // Exclamation mark
      ctx.fillStyle = '#0A1020';
      const barW = w * 0.15;
      ctx.fillRect(x + w / 2 - barW / 2, y + h * 0.2, barW, h * 0.5);
      ctx.fillRect(x + w / 2 - barW / 2, y + h * 0.75, barW, h * 0.15);
      break;
    }
    case 'error': {
      // X mark
      ctx.strokeStyle = '#0A1020';
      ctx.lineWidth = h * 0.3;
      ctx.lineCap = 'square';
      ctx.beginPath();
      ctx.moveTo(x + w * 0.25, y + h * 0.25);
      ctx.lineTo(x + w * 0.75, y + h * 0.75);
      ctx.moveTo(x + w * 0.75, y + h * 0.25);
      ctx.lineTo(x + w * 0.25, y + h * 0.75);
      ctx.stroke();
      break;
    }
    case 'offline': {
      // Single horizontal line (visor off)
      ctx.fillStyle = '#1D465E';
      ctx.fillRect(x, y + h * 0.4, w, h * 0.2);
      break;
    }
    case 'sleeping': {
      // Z letter (small, top-right)
      ctx.fillStyle = hexToRgba(color, 0.7);
      ctx.font = `${h * 1.2}px monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const zAlpha = 0.5 + 0.5 * Math.sin(frame * Math.PI * 0.25);
      ctx.globalAlpha = zAlpha;
      ctx.fillText('z', x + w * 0.7, y - h * 0.3);
      break;
    }
    case 'idle':
    case 'waiting_confirmation': {
      // Stable bar — no extra pattern
      break;
    }
  }

  ctx.restore();
}

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
